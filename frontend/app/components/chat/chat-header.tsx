import { Button } from "@/app/components/ui/button";
import { useBotStore } from "@/app/store/bot";
import { Undo2 } from "lucide-react";
import Locale from "../../locales";
import { useSidebarContext } from "../home";
import { Separator } from "../ui/separator";
import Typography from "../ui/typography";

export default function ChatHeader() {
  const { setShowSidebar } = useSidebarContext();
  const botStore = useBotStore();
  const bot = botStore.currentBot();
  const session = botStore.currentSession();
  const numberOfMessages = 0;
    //(bot.botHello?.length ? 1 : 0) + session.messages.length;
  return (
    <div className="relative">
      <div className="absolute top-4 left-5">
        {false && (
          <Button
            size="icon"
            variant="outline"
            title={Locale.Chat.Actions.ChatList}
            onClick={() => setShowSidebar(true)}
          >
            <Undo2 />
          </Button>
        )}
      </div>
      <div className="text-center py-4">
        <Typography.H4>{bot? bot.name : "no bot"}</Typography.H4>
        <div className="text-sm text-muted-foreground">
          {Locale.Chat.SubTitle(numberOfMessages)}
        </div>
      </div>
      <Separator />
    </div>
  );
}
