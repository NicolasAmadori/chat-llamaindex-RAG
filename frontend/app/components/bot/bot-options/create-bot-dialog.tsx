import Locale from "../../../locales";
import { DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "../../ui/dialog";
import { ScrollArea } from "../../ui/scroll-area";
import { Separator } from "../../ui/separator";
import { Button } from "../../ui/button"
import BotSettings from "../bot-settings";
import { useBotStore } from "../../../store/bot";
import { LLMConfig, LLMApi } from "../../../client/platforms/llm";

export default function CreateBotDialogContent() {
  const botStore = useBotStore();

  const onSubmitClick = async () => {
    // controllo se il bot ià esiste back end
    // se non esiste
    const bots = botStore.getAll()
    const lastAddedBot = bots[0]

    try{
      await LLMApi.create(lastAddedBot)
    }
    catch(err){
      console.log("Bot already exists")
      botStore.delete(lastAddedBot.id)
    }
  }

  return (
    <DialogContent className="max-w-4xl">
      <DialogHeader>
        <DialogTitle>Create a new bot</DialogTitle>
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
