"use client";
// React Context holding the CustomProject + persistence.
import { createContext, useContext, useEffect, useState, useCallback, ReactNode } from "react";
import { CustomProject, newProject, BlockDef, Stage, BgmTrack } from "./types";
import { loadProject, saveProject } from "./persist";

interface Ctx {
  project: CustomProject;
  setProject: (p: CustomProject) => void;
  updateStage: (i: number, s: Stage) => void;
  addStage: (s: Stage) => void;
  deleteStage: (i: number) => void;
  addBlock: (b: BlockDef) => void;
  updateBlock: (i: number, b: BlockDef) => void;
  deleteBlock: (i: number) => void;
  setBgm: (name: string, t: BgmTrack) => void;
  deleteBgm: (name: string) => void;
}

const ProjectContext = createContext<Ctx | null>(null);

export function ProjectProvider({ children }: { children: ReactNode }) {
  const [project, setProjectState] = useState<CustomProject>(newProject());
  const [loaded, setLoaded] = useState(false);

  useEffect(() => {
    setProjectState(loadProject());
    setLoaded(true);
  }, []);

  useEffect(() => {
    if (loaded) saveProject(project);
  }, [project, loaded]);

  const setProject = (p: CustomProject) => setProjectState(p);

  const updateStage = useCallback((i: number, s: Stage) => {
    setProjectState((prev) => {
      const stages = [...prev.stages];
      stages[i] = s;
      return { ...prev, stages };
    });
  }, []);

  const addStage = useCallback((s: Stage) => {
    setProjectState((prev) => ({ ...prev, stages: [...prev.stages, s] }));
  }, []);

  const deleteStage = useCallback((i: number) => {
    setProjectState((prev) => {
      const stages = prev.stages.filter((_, idx) => idx !== i);
      return { ...prev, stages };
    });
  }, []);

  const addBlock = useCallback((b: BlockDef) => {
    setProjectState((prev) => ({ ...prev, blocks: [...prev.blocks, b] }));
  }, []);

  const updateBlock = useCallback((i: number, b: BlockDef) => {
    setProjectState((prev) => {
      const blocks = [...prev.blocks];
      blocks[i] = b;
      return { ...prev, blocks };
    });
  }, []);

  const deleteBlock = useCallback((i: number) => {
    setProjectState((prev) => {
      const blocks = prev.blocks.filter((_, idx) => idx !== i);
      return { ...prev, blocks };
    });
  }, []);

  const setBgm = useCallback((name: string, t: BgmTrack) => {
    setProjectState((prev) => ({ ...prev, bgm: { ...prev.bgm, [name]: t } }));
  }, []);

  const deleteBgm = useCallback((name: string) => {
    setProjectState((prev) => {
      const { [name]: _gone, ...rest } = prev.bgm;
      return { ...prev, bgm: rest };
    });
  }, []);

  return (
    <ProjectContext.Provider
      value={{
        project,
        setProject,
        updateStage,
        addStage,
        deleteStage,
        addBlock,
        updateBlock,
        deleteBlock,
        setBgm,
        deleteBgm,
      }}
    >
      {children}
    </ProjectContext.Provider>
  );
}

export function useProject() {
  const v = useContext(ProjectContext);
  if (!v) throw new Error("ProjectProvider missing");
  return v;
}
