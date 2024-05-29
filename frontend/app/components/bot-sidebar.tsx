import { ThemeToggle } from "@/app/components/layout/theme-toggle";
import { Github, Settings } from "lucide-react";
import dynamic from "next/dynamic";
import { useNavigate } from "react-router-dom";
import { GITHUB_URL, Path } from "../../constants";
import Locale from "../locales";
import { Button } from "./ui/button";
import Typography from "./ui/typography";
import { useSidebarContext } from "@/app/components/home";

const BotList = dynamic(async () => (await import("./bot/bot-list")).default, {
  loading: () => null,
});

export function BotSideBar(props: { className?: string }) {
  const navigate = useNavigate();
  const { setShowSidebar } = useSidebarContext();

  return (
    <div className="h-full relative group border-r w-full md:w-[500px] border-l">
      <div className="w-full h-full p-5 flex flex-col gap-5">
        <div className="flex flex-col flex-1">
          <div className="mb-5 flex justify-center gap-5 items-start">
            <Typography.H1>Source</Typography.H1>
          </div>
        </div>
        <div className="flex items-center justify-end">
          <Button
            variant="outline"
            size="sm"
            onClick={() => window.open(GITHUB_URL, "_blank")}
          >
            <Github className="mr-2 h-4 w-4" />
            <span>{Locale.Home.Github}</span>
          </Button>
        </div>
      </div>
    </div>
  );
}