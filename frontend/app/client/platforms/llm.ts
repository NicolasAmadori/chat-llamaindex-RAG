import { REQUEST_TIMEOUT_MS, BASE_API_URL } from "../../../constants";

import { fetchEventSource } from "@fortaine/fetch-event-source";
import { Embedding } from "../fetch/url";

import { Bot } from "../../store/bot"

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

const CHAT_PATH = "/api/llm";

export function isVisionModel(model: ModelType) {
  return model === "gpt-4-vision-preview";
}

export class LLMApi {
  static async chat(options: ChatOptions) {
    const requestPayload = {
      message: options.message,
      chatHistory: options.chatHistory.map((m) => ({
        role: m.role,
        content: m.content,
      })),
      config: options.config,
      datasource: options.datasource,
      embeddings: options.embeddings,
    };

    console.log("[Request] payload: ", requestPayload);

    const requestTimeoutId = setTimeout(
      () => options.controller?.abort(),
      REQUEST_TIMEOUT_MS,
    );

    options.controller.signal.onabort = () => options.onFinish();
    const handleError = (e: any) => {
      clearTimeout(requestTimeoutId);
      console.log("[Request] failed to make a chat request", e);
      options.onError?.(e as Error);
    };

    try {
      const chatPayload = {
        method: "POST",
        body: JSON.stringify(requestPayload),
        signal: options.controller?.signal,
        headers: {
          "Content-Type": "application/json",
        },
      };

      let llmResponse = "";
      await fetchEventSource(CHAT_PATH, {
        ...chatPayload,
        async onopen(res) {
          clearTimeout(requestTimeoutId);
          if (!res.ok) {
            const json = await res.json();
            handleError(new Error(json.message));
          }
        },
        onmessage(msg) {
          try {
            const json = JSON.parse(msg.data);
            if (json.done) {
              options.onFinish(json.memoryMessage);
            } else if (json.error) {
              options.onError?.(new Error(json.error));
            } else {
              // received a new token
              llmResponse += json;
              options.onUpdate(llmResponse);
            }
          } catch (e) {
            console.error("[Request] error parsing streaming delta", msg);
          }
        },
        onclose() {
          options.onFinish();
        },
        onerror: handleError,
        openWhenHidden: true,
      });
    } catch (e) {
      handleError(e);
    }
  }

  static async create(bot: Bot) {
    const url = BASE_API_URL + "/bot/"

    const topP = bot.modelConfig.topP ? bot.modelConfig.topP : 1;

    const body = JSON.stringify({
      bot: {
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
    } catch(error) {
      console.error("Error in bot create: ", error);
    } 
  }
}
