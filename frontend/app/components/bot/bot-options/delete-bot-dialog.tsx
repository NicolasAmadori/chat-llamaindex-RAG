import { cn } from "@/app/lib/utils";
import Locale from "../../../locales";
import {
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "../../ui/alert-dialog";
import { useBot } from "../use-bot";
import { buttonVariants } from "@/app/components/ui/button";
import { LLMConfig, LLMApi } from "../../../client/platforms/llm";


export default function DeleteBotDialogContent() {
  const { deleteBot, bot } = useBot();

  const deleteBotApi = async () => {
    console.log("DELETING",bot)
    deleteBot()
    await LLMApi.delete(bot.id);
  }


  return (
    <AlertDialogContent>
      <AlertDialogHeader>
        <AlertDialogTitle>Are you absolutely sure?</AlertDialogTitle>
        <AlertDialogDescription>
          {Locale.Bot.Item.DeleteConfirm}
        </AlertDialogDescription>
      </AlertDialogHeader>
      <AlertDialogFooter>
        <AlertDialogCancel>Cancel</AlertDialogCancel>
        <AlertDialogAction
          className={cn(buttonVariants({ variant: "destructive" }))}
          onClick={deleteBotApi}
        >
          Continue
        </AlertDialogAction>
      </AlertDialogFooter>
    </AlertDialogContent>
  );
}
