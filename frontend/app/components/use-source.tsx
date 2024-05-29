import { createContext, useContext } from "react";
import { Source } from "./bot-sidebar";

const SourceItemContext = createContext<{
  source: Source;
}>({} as any);

export const SourceItemContextProvider = (props: {
  source: Source;
  children: JSX.Element;
}) => {
  const source = props.source;
  

  return (
    <SourceItemContext.Provider
      value={{
        source,
      }}
    >
      {props.children}
    </SourceItemContext.Provider>
  );
};

export const useSource = () => useContext(SourceItemContext);