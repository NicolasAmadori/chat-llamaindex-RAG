import { Bot } from "@/app/store/bot";
import { nanoid } from "nanoid";
import Locale from "../locales";
import { ModelType, DEFAULT_MODEL } from "@/app/client/platforms/llm";
import { createEmptySession } from "../store";

const TEMPLATE = (PERSONA: string) =>
  `I want you to act as a ${PERSONA}. I will provide you with the context needed to solve my problem. Use intelligent, simple, and understandable language. Be concise. It is helpful to explain your thoughts step by step and with bullet points.`;

type DemoBot = Omit<Bot, "session">;

export const DEMO_BOTS: DemoBot[] = [
  // {
  //   id: "5",
  //   avatar: "1f4da",
  //   name: "German Basic Law Expert",
  //   botHello: "Hello! How can I assist you today?",
  //   context: [
  //     {
  //       role: "system",
  //       content: TEMPLATE("Lawyer specialized in the basic law of Germany"),
  //     },
  //   ],
  //   modelConfig: {
  //     model: "gpt-4-1106-preview",
  //     temperature: 0.1,
  //     maxTokens: 4096,
  //     sendMemory: true,
  //   },
  //   readOnly: true,
  //   datasource: "basic_law_germany",
  //   hideContext: false,
  // }
];

export const createDemoBots = (): Record<string, Bot> => {
  const map: Record<string, Bot> = {};
  DEMO_BOTS.forEach((demoBot) => {
    const bot: Bot = JSON.parse(JSON.stringify(demoBot));
    //bot.session = createEmptySession();
    map[bot.id] = bot;
  });
  return map;
};

export const createEmptyBot = (): Bot => ({
  id: nanoid(),
  name: Locale.Store.DefaultBotName,
  modelName: DEFAULT_MODEL,
  context: [],
  modelConfig: {
    model: DEFAULT_MODEL as ModelType,
    temperature: 0.7,
    topP: 1,
    maxTokens: 2048,
    sendMemory: true,
    maxHistory: 2048
  },
  createdAt: Date.now(),
  botHello: Locale.Store.BotHello,
  hideContext: false,
  session: createEmptySession()
});