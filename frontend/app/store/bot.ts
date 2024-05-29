import { nanoid } from "nanoid";
import { create } from "zustand";
import { persist } from "zustand/middleware";
import { LLMConfig, LLMApi } from "../client/platforms/llm";
import { ChatSession, ChatMessage, createEmptySession } from "./session";
import { DEMO_BOTS, createDemoBots, createEmptyBot } from "@/app/bots/bot.data";

export type Share = {
  id: string;
};

// TODO: fix bot to match back end

export type Bot = {
  id: string;
  // avatar: string; // To Remove
  name: string; // is bot name
  modelName: string; // To configure
  hideContext: boolean; 
  context: ChatMessage[];
  modelConfig: LLMConfig;
  // readOnly: boolean; // To Remove
  botHello: string | null; 
  datasource?: string;
  // share?: Share; // To Remove
  createdAt?: number;
  session: ChatSession; // To Remove
};

type BotState = {
  bots: Record<string, Bot>;
  currentBotId: string;
};

// TODO: fix bot store and functions
type BotStore = BotState & {
  currentBot: () => Bot;
  selectBot: (id: string) => void;
  currentSession: () => ChatSession;
  updateBotSession: (
    updater: (session: ChatSession) => void,
    botId: string,
  ) => void;
  get: (id: string) => Bot | undefined;
  // getByShareId: (shareId: string) => Bot | undefined;
  getAll: () => Bot[];
  create: (
    bot?: Partial<Bot>,
    options?: { readOnly?: boolean; reset?: boolean },
  ) => Promise<Bot>;
  update: (old_id: string,new_id:string, updater: (bot: Bot) => void) => void;
  delete: (id: string) => void;
  restore: (state: BotState) => void;
  backup: () => BotState;
  clearAllData: () => void;
};

const demoBots = createDemoBots();

export const useBotStore = create<BotStore>()(
  persist(
    (set, get) => ({
      bots: demoBots,
      currentBotId: "-1",//Object.values(demoBots)[0].id,

      currentBot() {
        if (get().currentBotId === "-1") {
          // Create a new empty bot if no bot is present
          const newBot = createEmptyBot();
          const id = nanoid();
          newBot.id = id;
          set((state) => ({
            bots: {
              ...state.bots,
              [id]: newBot,
            },
            currentBotId: id,
          }));
          return newBot;
        }
        return get().bots[get().currentBotId];
      },
      selectBot(id) {
        set(() => ({ currentBotId: id }));
      },
      currentSession() {
        //return get().currentBot().session;
        let session = createEmptySession(); 
        if (get().currentBotId == "-1") {
          return session;
        }
        session = get().currentBot().session
        return session;
      },
      updateBotSession(updater, botId) {
        const bots = get().bots;
        if (!bots[botId]) return;
        updater(bots[botId].session);
        set(() => ({ bots }));
      },
      get(id) {
        return get().bots[id] || undefined;
      },
      getAll() {
        const list = Object.values(get().bots).map((b) => ({
          ...b,
          createdAt: b.createdAt || 0,
        }));
        return list.sort((a, b) => b.createdAt - a.createdAt);
      },
      // getByShareId(shareId) {
      //   return get()
      //     .getAll()
      //     .find((b) => shareId === b.share?.id);
      // },
      async create(bot, options) {
        const bots = get().bots;
        const id = nanoid();
        bots[id] = {
          ...createEmptyBot(),
          ...bot,
          id,
          session: createEmptySession()
        };

        set(() => ({ bots }));
        return bots[id];
      },
      update(old_id, new_id, updater) {
        const bots = get().bots;
        const bot = bots[old_id];
        if (!bot) return;
        const updateBot = { ...bot };
        updater(updateBot);
        bots[new_id] = updateBot;
        set(() => ({ bots }));
        if(old_id !== new_id){
          this.delete(old_id)
          console.log("Deleting")
        }
      },
      delete(id) {
        const bots = JSON.parse(JSON.stringify(get().bots));
        delete bots[id];
        let nextId = get().currentBotId;
        if (nextId === id) {
          if(Object.keys(bots).length > 0){
            nextId = Object.keys(bots)[0];
          }else{
            nextId = "-1";
          }
        }
        set(() => ({ bots, currentBotId: nextId }));
      },

      backup() {
        return get();
      },
      restore(state: BotState) {
        if (!state.bots) {
          throw new Error("no state object");
        }
        set(() => ({ bots: state.bots }));
      },
      clearAllData() {
        for (const bot of Object.values(get().bots)) {
          LLMApi.delete(bot.id);
        }
        localStorage.clear();
        location.reload();
      }
    }),
    {
      name: "bot-store",
      version: 1,
      migrate: (persistedState, version) => {
        const state = persistedState as BotState;
        if (version < 1) {
          DEMO_BOTS.forEach((demoBot) => {
            // check if there is a bot with the same name as the demo bot
            const bot = Object.values(state.bots).find(
              (b) => b.name === demoBot.name,
            );
            if (bot) {
              // if so, update the id of the bot to the demo bot id
              delete state.bots[bot.id];
              bot.id = demoBot.id;
              state.bots[bot.id] = bot;
            } else {
              // if not, store the new demo bot
              const bot: Bot = JSON.parse(JSON.stringify(demoBot));
              state.bots[bot.id] = bot;
            }
          });
          state.currentBotId = Object.values(state.bots)[0].id;
        }
        return state as any;
      },
    },
  ),
);