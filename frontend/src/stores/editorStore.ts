import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { EditorState, GenerationTask } from '@/types';

const initialState = {
  // Image state
  originalImage: null,
  generatedImage: null,
  imageId: null,
  isUploading: false,
  isGenerating: false,
  
  // Generation parameters
  prompt: '',
  negativePrompt: '',
  style: 'default',
  strength: 0.75,
  steps: 30,
  
  // Task state
  taskId: null,
  taskStatus: null,
  taskProgress: 0,
  error: null,
};

export const useEditorStore = create<EditorState>()(
  persist(
    (set) => ({
      ...initialState,
      
      // Actions
      setOriginalImage: (url) => set({ originalImage: url }),
      setGeneratedImage: (url) => set({ generatedImage: url }),
      setImageId: (id) => set({ imageId: id }),
      setIsUploading: (isUploading) => set({ isUploading }),
      setIsGenerating: (isGenerating) => set({ isGenerating }),
      setPrompt: (prompt) => set({ prompt }),
      setNegativePrompt: (prompt) => set({ negativePrompt: prompt }),
      setStyle: (style) => set({ style }),
      setStrength: (strength) => set({ strength }),
      setSteps: (steps) => set({ steps }),
      setTaskId: (id) => set({ taskId: id }),
      setTaskStatus: (status) => set({ taskStatus: status }),
      setTaskProgress: (progress) => set({ taskProgress: progress }),
      setError: (error) => set({ error }),
      reset: () => set({ ...initialState }),
    }),
    {
      name: 'ai-image-editor-storage',
      partialize: (state) => ({
        style: state.style,
        strength: state.strength,
        steps: state.steps,
      }),
    }
  )
);
