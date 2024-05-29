import { Button } from "@/app/components/ui/button";
import { useBotStore } from "@/app/store/bot";
import { Undo2 } from "lucide-react";
import Locale from "../../locales";
import { useSidebarContext } from "../home";
import { Separator } from "../ui/separator";
import Typography from "../ui/typography";
import { ThemeToggle } from "../layout/theme-toggle";

import { Settings } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { Path } from "../../../constants";

export default function ChatHeader() {
  const { setShowSidebar } = useSidebarContext();
  const botStore = useBotStore();
  const bot = botStore.currentBot();
  const session = botStore.currentSession();
  const numberOfMessages = bot ? (bot.botHello?.length ? 1 : 0) + session.messages.length : 0;
  const navigate = useNavigate();
  return (
    <div className="relative">
      <div className="absolute top-4 left-5">
        <ThemeToggle />
      </div>
      <div className="text-center py-4">
        <Typography.H1>CLVZ LlamaIndex</Typography.H1>
        <Typography.P>{bot? "Using "+bot.modelConfig.model : ""}</Typography.P>
        {bot && <div className="text-sm text-muted-foreground">
          {Locale.Chat.SubTitle(numberOfMessages)}
        </div>}
      </div>
      <div className="absolute top-4 right-5">
        <Button
            variant="secondary"
            size="icon"
            onClick={() => {
              navigate(Path.Settings);
              setShowSidebar(false);
            }}
          >
            <Settings className="h-4 w-4" />
          </Button>
      </div>
      <Separator />
    </div>
  );
}
