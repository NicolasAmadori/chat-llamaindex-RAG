import { REQUEST_TIMEOUT_MS, BASE_API_URL } from "../../../constants";

import { fetchEventSource } from "@fortaine/fetch-event-source";
import { Embedding } from "../fetch/url";

import { Bot } from "../../store/bot"
import { nanoid } from "nanoid";

export const MESSAGE_ROLES = [
  "system",
  "user",
  "assistant",
  "URL",
  "memory",
] as const;
export type MessageRole = (typeof MESSAGE_ROLES)[number];

export interface MessageContentDetail {
  type: "text" | "image_url";
  text: string;
  image_url: { url: string };
}

export type MessageContent = string | MessageContentDetail[];

export interface RequestMessage {
  role: MessageRole;
  content: MessageContent;
}

export interface ResponseMessage {
  role: MessageRole;
  content: string;
}

export let ALL_MODELS = []
export let DEFAULT_MODEL = ""

const load_models = async () => {
  const url = BASE_API_URL + "/bot/available_models"
  const available_models = await fetch(url).then((res) => res.json());
  const modelcards = available_models.map((x: any) => x.modelcard)

  ALL_MODELS = modelcards
  DEFAULT_MODEL = modelcards[0]
} 

const ALL_MODELS_PROMISE = (async () => {
  await load_models()
})()

ALL_MODELS_PROMISE.then((models) => models)

export type ModelType = typeof ALL_MODELS[number];

export interface LLMConfig {
  model: ModelType;
  temperature?: number;
  topP?: number;
  sendMemory?: boolean;
  maxTokens?: number;
  maxHistory?: number;
}

export interface ChatOptions {
  bot_id: string;
  message: MessageContent;
  chatHistory: RequestMessage[];
  config: LLMConfig;
  datasource?: string;
  embeddings?: Embedding[];
  controller: AbortController;
  onUpdate: (message: string) => void;
  onFinish: (memoryMessage?: ResponseMessage) => void;
  onError?: (err: Error) => void;
}


export function isVisionModel(model: ModelType) {
  return model === "gpt-4-vision-preview";
}

export class LLMApi {
  static async chat(options: ChatOptions) {
    console.log("OPTION,", options)

    const url = BASE_API_URL + "/chat";


    let messages = options.chatHistory.map((m) => ({
      role: m.role,
      content: m.content,
    }))
    messages.push({
      role: "user",
      content: options.message
    })

    const requestPayload = {
      messages: messages,
      bot_id: options.bot_id,
    }

    console.log("[Request] payload: ", requestPayload);

    const body = JSON.stringify(requestPayload)
    let response = {}

    try{
      response = await fetch(url, {
        method: "POST", // or 'PUT'
        headers: {
          "Content-Type": "application/json",
        },
        body: body
      });
    }
    catch(error){
      console.error(error)
    }

    console.log("Oltre la richiesta");

    if (response.body) {
      const reader = response.body.getReader();
      let receivedLength = 0; // length of received data
      let chunks = []; // array to store received chunks
      
      while(true) {
        const { done, value } = await reader.read();
    
        if (done) {
          break;
        }
    
        chunks.push(value);
        receivedLength += value.length;
        console.log(chunks)
      }
    
      let chunksAll = new Uint8Array(receivedLength); // create a new array to store all chunks
      let position = 0;
      for(let chunk of chunks) {
        chunksAll.set(chunk, position); // copy data from each chunk to the new array
        position += chunk.length;
      }
    
      let result = new TextDecoder("utf-8").decode(chunksAll);
      // Now 'result' contains the complete response body as a string
      console.log(result);
    } else {
      console.log("No response body");
    }

  }

  static async create(bot: Bot) {
    console.log("API CREATE")

    const url = BASE_API_URL + "/bot/"

    const topP = bot.modelConfig.topP ? bot.modelConfig.topP : 1;

    const body = JSON.stringify({
      bot: {
        bot_id: bot.id,
        bot_name: bot.name,
        model_name: bot.modelName,
        hide_context: bot.hideContext,
        context: bot.context,
        model_config: {
          maxHistory: bot.modelConfig.maxHistory,
          maxTokens: bot.modelConfig.maxTokens,
          topP: bot.modelConfig.topP,
          model_name: bot.modelConfig.model,
          temperature: bot.modelConfig.temperature,
          sendMemory: bot.modelConfig.sendMemory
        },
        bot_hello: bot.botHello,
        data_source: "",
      }
    })

    console.log(body)

    try {
      const response = await fetch(url, {
        method: "POST", // or 'PUT'
        headers: {
          "Content-Type": "application/json",
        },
        body: body
      });

      if (!response.ok){
        throw new Error(`HTTP error! status: ${response.status}`);
      }

    } catch(error) {
      console.error("Error in bot create: ", error);
      throw error;
    } 
  }

  static async delete(bot_id: string) {
    console.log("API DELETE")

    const url = BASE_API_URL + "/bot/"
    try {
      const response = await fetch(url, {
        method: "DELETE", // or 'PUT'
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          bot_id: bot_id,
        })
      });

      if (!response.ok){
        throw new Error(`HTTP error! status: ${response.status}`);
      }

    } catch(error) {
      console.error("Error in bot delete: ", error);
      throw error;
    } 
  }

  static async patch(old_id: string, bot: Bot) {
    console.log("API PATCH")
    await LLMApi.delete(old_id);
    await LLMApi.create(bot);
  }
}
