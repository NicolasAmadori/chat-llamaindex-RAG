import { Source } from "./bot-sidebar";
import { SourceItemContextProvider, useSource } from "./use-source";

function SourceItemUI() {
  const { source } = useSource();
  return (
    <div
      className="flex items-center cursor-pointer mb-2 last:mb-0 rounded-md border-2 border-muted bg-popover hover:bg-accent hover:text-accent-foreground relative p-4 pr-12"
    >
      <div className="w-[18px] h-[18px] mr-2">
        {/* <BotAvatar avatar={bot.avatar} /> */}
      </div>
      <div className="flex flex-col w-full">
        <div className="font-medium">{source.text}</div>
        <div className="text-sm text-muted-foreground">
          {source.author} - {source.date ? new Date(source.date).toLocaleDateString() : "Data non disponibile"}
        </div>
        <div className="text-sm text-blue-600">
          <a href={source.link} target="_blank" rel="noopener noreferrer">Leggi di più</a>
        </div>
      </div>
    </div>
  );
}

export default function SourceItem(props: { source: Source }) {
  return (
    <SourceItemContextProvider source={props.source}>
      <SourceItemUI />
    </SourceItemContextProvider>
  );
}
