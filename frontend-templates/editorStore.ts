// frontend/src/stores/editorStore.ts
import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';

interface EditorState {
  // 图片状态
  originalImage: string | null;
  originalImageId: string | null;
  generatedImage: string | null;
  isUploading: boolean;
  isGenerating: boolean;
  generationProgress: number;

  // 编辑参数
  prompt: string;
  negativePrompt: string;
  style: string;
  strength: number;
  steps: number;
  guidanceScale: number;

  // 错误状态
  error: string | null;
}

interface EditorActions {
  // 图片操作
  setOriginalImage: (url: string, id: string) => void;
  setGeneratedImage: (url: string | null) => void;
  setIsUploading: (value: boolean) => void;
  setIsGenerating: (value: boolean) => void;
  setGenerationProgress: (progress: number) => void;

  // 参数操作
  setPrompt: (prompt: string) => void;
  setNegativePrompt: (prompt: string) => void;
  setStyle: (style: string) => void;
  setStrength: (strength: number) => void;
  setSteps: (steps: number) => void;
  setGuidanceScale: (scale: number) => void;

  // 错误操作
  setError: (error: string | null) => void;

  // 重置
  reset: () => void;
  resetGenerated: () => void;
}

const initialState: EditorState = {
  originalImage: null,
  originalImageId: null,
  generatedImage: null,
  isUploading: false,
  isGenerating: false,
  generationProgress: 0,
  prompt: '',
  negativePrompt: '',
  style: 'default',
  strength: 0.75,
  steps: 30,
  guidanceScale: 7.5,
  error: null,
};

export const useEditorStore = create<EditorState & EditorActions>()(
  devtools(
    persist(
      (set) => ({
        ...initialState,

        // 图片操作
        setOriginalImage: (url, id) =>
          set({ originalImage: url, originalImageId: id }),
        setGeneratedImage: (url) => set({ generatedImage: url }),
        setIsUploading: (value) => set({ isUploading: value }),
        setIsGenerating: (value) => set({ isGenerating: value }),
        setGenerationProgress: (progress) =>
          set({ generationProgress: progress }),

        // 参数操作
        setPrompt: (prompt) => set({ prompt }),
        setNegativePrompt: (prompt) => set({ negativePrompt: prompt }),
        setStyle: (style) => set({ style }),
        setStrength: (strength) => set({ strength }),
        setSteps: (steps) => set({ steps }),
        setGuidanceScale: (scale) => set({ guidanceScale: scale }),

        // 错误操作
        setError: (error) => set({ error }),

        // 重置
        reset: () => set(initialState),
        resetGenerated: () =>
          set({ generatedImage: null, generationProgress: 0, error: null }),
      }),
      {
        name: 'editor-storage',
        partialize: (state) => ({
          style: state.style,
          strength: state.strength,
          steps: state.steps,
          guidanceScale: state.guidanceScale,
        }),
      }
    )
  )
);
