import { get, post, postForm, del } from './client';
import type { 
  UploadedImage, 
  GenerationParams, 
  GenerationTask 
} from '@/types';

// Upload image
export async function uploadImage(file: File, onProgress?: (progress: number) => void): Promise<UploadedImage> {
  const formData = new FormData();
  formData.append('file', file);
  
  return postForm<UploadedImage>('/images/upload', formData, {
    onUploadProgress: (progressEvent) => {
      if (progressEvent.total && onProgress) {
        const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total);
        onProgress(progress);
      }
    },
  });
}

// Generate image
export async function generateImage(params: GenerationParams): Promise<GenerationTask> {
  return post<GenerationTask>('/images/generate', params);
}

// Get task status
export async function getTaskStatus(taskId: string): Promise<GenerationTask> {
  return get<GenerationTask>(`/images/status/${taskId}`);
}

// Poll task status until completion
export async function pollTaskStatus(
  taskId: string, 
  onProgress?: (task: GenerationTask) => void,
  interval: number = 1000
): Promise<GenerationTask> {
  return new Promise((resolve, reject) => {
    const poll = async () => {
      try {
        const task = await getTaskStatus(taskId);
        
        if (onProgress) {
          onProgress(task);
        }
        
        if (task.status === 'completed') {
          resolve(task);
        } else if (task.status === 'failed') {
          reject(new Error(task.error || '生成失败'));
        } else {
          setTimeout(poll, interval);
        }
      } catch (error) {
        reject(error);
      }
    };
    
    poll();
  });
}

// Download image
export function getImageDownloadUrl(imageId: string): string {
  return `/api/v1/images/download/${imageId}`;
}

// Delete image
export async function deleteImage(imageId: string): Promise<void> {
  await del(`/images/${imageId}`);
}

// Validate image file
export function validateImageFile(file: File): { valid: boolean; error?: string } {
  // Check file type
  const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp'];
  if (!allowedTypes.includes(file.type)) {
    return { valid: false, error: '请上传 JPG、PNG 或 WebP 格式的图片' };
  }
  
  // Check file size (10MB)
  const maxSize = 10 * 1024 * 1024;
  if (file.size > maxSize) {
    return { valid: false, error: '图片大小不能超过 10MB' };
  }
  
  return { valid: true };
}

// Create image preview URL
export function createImagePreview(file: File): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => {
      resolve(reader.result as string);
    };
    reader.onerror = () => {
      reject(new Error('无法读取图片文件'));
    };
    reader.readAsDataURL(file);
  });
}
