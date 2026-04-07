// Image types
export interface ImageFile {
  id: string;
  file: File;
  preview: string;
  url?: string;
}

export interface UploadedImage {
  image_id: string;
  url: string;
}

// Generation types
export interface GenerationParams {
  image_id: string;
  prompt: string;
  negative_prompt?: string;
  style?: string;
  strength?: number;
  steps?: number;
}

export interface GenerationTask {
  task_id: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  progress?: number;
  result_url?: string;
  error?: string;
}

// Editor state types
export interface EditorState {
  // Image state
  originalImage: string | null;
  generatedImage: string | null;
  imageId: string | null;
  isUploading: boolean;
  isGenerating: boolean;
  
  // Generation parameters
  prompt: string;
  negativePrompt: string;
  style: string;
  strength: number;
  steps: number;
  
  // Task state
  taskId: string | null;
  taskStatus: GenerationTask['status'] | null;
  taskProgress: number;
  error: string | null;
  
  // Actions
  setOriginalImage: (url: string | null) => void;
  setGeneratedImage: (url: string | null) => void;
  setImageId: (id: string | null) => void;
  setIsUploading: (isUploading: boolean) => void;
  setIsGenerating: (isGenerating: boolean) => void;
  setPrompt: (prompt: string) => void;
  setNegativePrompt: (prompt: string) => void;
  setStyle: (style: string) => void;
  setStrength: (strength: number) => void;
  setSteps: (steps: number) => void;
  setTaskId: (id: string | null) => void;
  setTaskStatus: (status: GenerationTask['status'] | null) => void;
  setTaskProgress: (progress: number) => void;
  setError: (error: string | null) => void;
  reset: () => void;
}

// Style option types
export interface StyleOption {
  id: string;
  name: string;
  description: string;
  preview?: string;
}

// API response types
export interface ApiResponse<T> {
  data: T;
  message?: string;
  success: boolean;
}

export interface ApiError {
  message: string;
  code?: string;
  details?: Record<string, string[]>;
}
