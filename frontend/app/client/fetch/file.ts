import { URLDetailContent } from "./url";
import { FileWrap } from "../../utils/file";
import {
  ALLOWED_IMAGE_EXTENSIONS,
  BASE_API_URL,
  IMAGE_TYPES,
  ImageType,
} from "../../../constants";

export async function getDetailContentFromFile(
  file: FileWrap,
  bot_id:string
): Promise<URLDetailContent> {
  if (file.extension === "pdf") return await getPDFFileDetail(file, bot_id);
  if (file.extension === "txt") return await getTextFileDetail(file, bot_id);
  if (ALLOWED_IMAGE_EXTENSIONS.includes(file.extension))
    return await getImageFileDetail(file);
  throw new Error("Not supported file type");
}

const url = BASE_API_URL + "/file"

async function getPDFFileDetail(file: FileWrap, bot_id: string): Promise<URLDetailContent> {
  const fileDataUrl = await file.readData({ asURL: true });
  const pdfBase64 = fileDataUrl.split(",")[1];
  const response = await fetch(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      bot_id: bot_id,
      file: pdfBase64,
      filename: file.name,
    }),
  });
  const data = await response.json();
  if (!response.ok) throw new Error(data.error);
  return data as URLDetailContent;
}

async function getTextFileDetail(file: FileWrap, bot_id: string): Promise<URLDetailContent> {
  const textContent = await file.readData();
  const response = await fetch(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      bot_id: bot_id,
      file: textContent,
      filename: file.name,
    }),
  });
  const data = await response.json();
  console.log(data);
  if (!response.ok) throw new Error(data.error);
  return data as URLDetailContent;
}

async function getImageFileDetail(file: FileWrap) {
  const response = await fetch(`/api/upload?filename=${file.name}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: file.file,
  });
  const data = await response.json();
  if (!response.ok) throw new Error(data.error);
  console.log(data);
  return data as URLDetailContent;
}

export const isImageFileType = (type: string) =>
  IMAGE_TYPES.includes(type as ImageType);
