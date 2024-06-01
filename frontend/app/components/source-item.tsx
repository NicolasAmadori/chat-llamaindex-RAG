import { Source } from "./bot-sidebar";
import { SourceItemContextProvider, useSource } from "./use-source";
import Locale from "../locales";
import "../styles/lib/highlight.css"
import { useEffect, useRef } from "react";

function SourceItemUI() {
  const { source } = useSource();
  const highlightText = (text: string, start: number, end: number) => {
    const beforeHighlight = text.substring(0, start);
    const highlighted = text.substring(start, end);
    const afterHighlight = text.substring(end);
    return (
      <>
        {beforeHighlight}
        <span className="bg-yellow-600 text-black">{highlighted}</span>
        {afterHighlight}
      </>
    );
  };
  const ref = useRef<any>(null);

  useEffect(() => {
    if (ref.current) {
      const highlightElement = ref.current.querySelector('.bg-yellow-600');
      if (highlightElement) {
        const elOffsetTop = highlightElement.offsetTop;
        const elHeight = highlightElement.offsetHeight / 2;
        const containerHeight = ref.current.offsetHeight / 2;
        ref.current.scrollTop = elOffsetTop - containerHeight;
      }
    }
  }, []);

  return (
    <div
      className="flex flex-col justify-start items-start cursor-pointer mb-2 last:mb-0 rounded-md border-2 border-muted bg-popover hover:bg-accent relative p-4 overflow-hidden"
    >
      <div className="w-full mb-2">
        <a href={source.link} target="_blank" rel="noopener noreferrer" className="card-link">
          <div className="card bg-blue-500 mb-2 p-2 rounded-md">
            <strong>{Locale.Home.SideBar.Source}: </strong> 
            {source.link}
          </div>
        </a>
        <div className="card bg-orange-500 mb-2 p-2 rounded-md">
          <strong>{Locale.Home.SideBar.Author}: </strong> <span className="card-author">{source.author}</span>
        </div>
      </div>
      <div 
        ref={ref}
        className="flex flex-col w-full max-h-60 overflow-y-auto rounded-md">
        <div className="font-medium">
          {highlightText(source.text, source.startHighlight, source.endHighlight)}
        </div>
      </div>
      {source.date != null && (
          <div className="rounded-md text-muted-foreground mt-2">
            <strong>{Locale.Home.SideBar.Date}: </strong> {new Date(source.date).toLocaleDateString()}
          </div>
        )}
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
