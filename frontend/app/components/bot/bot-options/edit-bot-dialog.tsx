import Locale from "../../../locales";
import { DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "../../ui/dialog";
import { ScrollArea } from "../../ui/scroll-area";
import { Separator } from "../../ui/separator";
import { Button } from "../../ui/button"
import BotSettings from "../bot-settings";
import { useBotStore } from "../../../store/bot";
import { LLMConfig, LLMApi } from "../../../client/platforms/llm";
import { Bot } from "../../../store/bot";
import { nanoid } from "nanoid";
import { Updater } from "@/app/typing";
import { useBot } from "../use-bot";


export default function EditBotDialogContent() {
  const botStore = useBotStore();
  const { bot } = useBot();

  console.log(bot)

  const onSubmitClick = async () => {
    try{
      const old_id = bot.id
      const new_id = nanoid()
      bot.id = new_id

      await LLMApi.patch(old_id, bot)
      botStore.update(
        old_id,
        new_id,
        (old_bot: Bot) => {
          old_bot.botHello = bot.botHello
          old_bot.context = bot.context
          old_bot.createdAt = bot.createdAt
          old_bot.datasource = bot.datasource
          old_bot.hideContext = bot.hideContext
          old_bot.id = bot.id
          old_bot.modelConfig = bot.modelConfig
          old_bot.modelName = bot.modelName
          old_bot.name = bot.name 
        }
      )
    }
    catch(err){
      console.log("Some error occured")
      botStore.delete(bot.id)
    }
  }

  return (
    <DialogContent className="max-w-4xl">
      <DialogHeader>
        <DialogTitle>{Locale.Bot.EditModal.Title}</DialogTitle>
      </DialogHeader>
      <Separator />
      <ScrollArea className="h-[50vh] mt-4 pr-4">
        <BotSettings />
      </ScrollArea>
      <DialogTrigger asChild>
        <Button onClick = { onSubmitClick }>Submit</Button>
      </DialogTrigger>
    </DialogContent>
  );
}
