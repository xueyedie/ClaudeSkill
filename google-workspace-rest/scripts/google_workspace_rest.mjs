#!/usr/bin/env node

import crypto from "node:crypto";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";

const DEFAULT_CONFIG_DIR = path.join(os.homedir(), ".config", "gws");
const TOKEN_ENDPOINT = "https://oauth2.googleapis.com/token";

function usage() {
  console.log(`Usage:
  node google_workspace_rest.mjs [--config-dir DIR] token-info
  node google_workspace_rest.mjs [--config-dir DIR] drive-list [--page-size N] [--query Q] [--fields F]
  node google_workspace_rest.mjs [--config-dir DIR] sheets-metadata <spreadsheet_id>
  node google_workspace_rest.mjs [--config-dir DIR] sheets-values <spreadsheet_id> <range>
  node google_workspace_rest.mjs [--config-dir DIR] docs-get <document_id>
  node google_workspace_rest.mjs [--config-dir DIR] calendar-events <calendar_id> [--time-min ISO] [--time-max ISO]
  node google_workspace_rest.mjs [--config-dir DIR] request <METHOD> <URL> [--body-json JSON]`);
}

function parseArgs(argv) {
  const args = [...argv];
  let configDir = DEFAULT_CONFIG_DIR;
  if (args[0] === "--config-dir") {
    configDir = args[1];
    args.splice(0, 2);
  }
  if (args.length === 0 || args[0] === "--help" || args[0] === "-h") {
    return { help: true, configDir };
  }
  return { help: false, configDir, command: args[0], rest: args.slice(1) };
}

function takeFlag(rest, name, fallback = null) {
  const idx = rest.indexOf(name);
  if (idx === -1) {
    return fallback;
  }
  const value = rest[idx + 1];
  rest.splice(idx, 2);
  return value;
}

function decryptCredentials(configDir) {
  const keyB64 = fs.readFileSync(path.join(configDir, ".encryption_key"), "utf8").trim();
  const key = Buffer.from(keyB64, "base64");
  const data = fs.readFileSync(path.join(configDir, "credentials.enc"));
  const nonce = data.subarray(0, 12);
  const ciphertext = data.subarray(12, data.length - 16);
  const tag = data.subarray(data.length - 16);
  const decipher = crypto.createDecipheriv("aes-256-gcm", key, nonce);
  decipher.setAuthTag(tag);
  const plaintext = Buffer.concat([decipher.update(ciphertext), decipher.final()]).toString("utf8");
  return JSON.parse(plaintext);
}

async function refreshAccessToken(creds) {
  const body = new URLSearchParams({
    client_id: creds.client_id,
    client_secret: creds.client_secret,
    refresh_token: creds.refresh_token,
    grant_type: "refresh_token",
  });
  const resp = await fetch(TOKEN_ENDPOINT, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body,
  });
  return await resp.json();
}

async function apiRequest(method, url, accessToken, bodyJson = null) {
  const headers = { Authorization: `Bearer ${accessToken}` };
  const init = { method, headers };
  if (bodyJson !== null) {
    headers["Content-Type"] = "application/json";
    init.body = JSON.stringify(bodyJson);
  }
  const resp = await fetch(url, init);
  const text = await resp.text();
  let json;
  try {
    json = text ? JSON.parse(text) : {};
  } catch {
    json = { raw: text };
  }
  if (!resp.ok) {
    json._http_status = resp.status;
  }
  return json;
}

function printJson(obj) {
  console.log(JSON.stringify(obj, null, 2));
}

function buildDriveListUrl(pageSize, query, fields) {
  const url = new URL("https://www.googleapis.com/drive/v3/files");
  url.searchParams.set("pageSize", String(pageSize));
  if (query) url.searchParams.set("q", query);
  if (fields) url.searchParams.set("fields", fields);
  return url.toString();
}

function buildSheetsMetadataUrl(spreadsheetId) {
  const url = new URL(`https://sheets.googleapis.com/v4/spreadsheets/${spreadsheetId}`);
  url.searchParams.set("fields", "properties.title,sheets.properties.title");
  return url.toString();
}

function buildSheetsValuesUrl(spreadsheetId, cellRange) {
  return `https://sheets.googleapis.com/v4/spreadsheets/${spreadsheetId}/values/${encodeURIComponent(cellRange)}`;
}

function buildDocsGetUrl(documentId) {
  return `https://docs.googleapis.com/v1/documents/${documentId}`;
}

function buildCalendarEventsUrl(calendarId, timeMin, timeMax) {
  const url = new URL(`https://www.googleapis.com/calendar/v3/calendars/${encodeURIComponent(calendarId)}/events`);
  url.searchParams.set("singleEvents", "true");
  url.searchParams.set("orderBy", "startTime");
  if (timeMin) url.searchParams.set("timeMin", timeMin);
  if (timeMax) url.searchParams.set("timeMax", timeMax);
  return url.toString();
}

async function main() {
  const parsed = parseArgs(process.argv.slice(2));
  if (parsed.help) {
    usage();
    process.exit(0);
  }

  const rest = [...parsed.rest];
  const creds = decryptCredentials(parsed.configDir);
  const token = await refreshAccessToken(creds);
  if (!token.access_token) {
    printJson(token);
    process.exit(1);
  }

  if (parsed.command === "token-info") {
    printJson({
      token_type: token.token_type ?? null,
      expires_in: token.expires_in ?? null,
      scope: token.scope ?? null,
      has_access_token: true,
    });
    return;
  }

  if (parsed.command === "drive-list") {
    const pageSize = Number(takeFlag(rest, "--page-size", "10"));
    const query = takeFlag(rest, "--query", "trashed=false");
    const fields = takeFlag(
      rest,
      "--fields",
      "files(id,name,mimeType,modifiedTime,webViewLink),nextPageToken",
    );
    printJson(await apiRequest("GET", buildDriveListUrl(pageSize, query, fields), token.access_token));
    return;
  }

  if (parsed.command === "sheets-metadata") {
    printJson(await apiRequest("GET", buildSheetsMetadataUrl(rest[0]), token.access_token));
    return;
  }

  if (parsed.command === "sheets-values") {
    printJson(await apiRequest("GET", buildSheetsValuesUrl(rest[0], rest[1]), token.access_token));
    return;
  }

  if (parsed.command === "docs-get") {
    printJson(await apiRequest("GET", buildDocsGetUrl(rest[0]), token.access_token));
    return;
  }

  if (parsed.command === "calendar-events") {
    const timeMin = takeFlag(rest, "--time-min");
    const timeMax = takeFlag(rest, "--time-max");
    printJson(await apiRequest("GET", buildCalendarEventsUrl(rest[0], timeMin, timeMax), token.access_token));
    return;
  }

  if (parsed.command === "request") {
    const method = rest[0];
    const url = rest[1];
    const bodyJsonRaw = takeFlag(rest, "--body-json");
    const bodyJson = bodyJsonRaw ? JSON.parse(bodyJsonRaw) : null;
    printJson(await apiRequest(method, url, token.access_token, bodyJson));
    return;
  }

  usage();
  process.exit(1);
}

main().catch((err) => {
  console.error(err?.stack || String(err));
  process.exit(1);
});
