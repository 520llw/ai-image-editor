import { useState, useCallback } from 'react';
import { generateImage, pollTaskStatus } from '@/api/imageApi';
import { useEditorStore } from '@/stores/editorStore';
import type { GenerationTask } from '@/types';

interface UseImageGenerationReturn {
  isGenerating: boolean;
  progress: number;
  generate: () => Promise<void>;
}

export function useImageGeneration(
  onSuccess?: () => void,
  onError?: (error: string) => void
): UseImageGenerationReturn {
  const [progress, setProgress] = useState(0);
  
  const {
    imageId,
    prompt,
    negativePrompt,
    style,
    strength,
    steps,
    setIsGenerating,
    setGeneratedImage,
    setTaskId,
    setTaskStatus,
    setTaskProgress,
    setError,
  } = useEditorStore();

  const generate = useCallback(async () => {
    if (!imageId) {
      const errorMsg = '请先上传图片';
      setError(errorMsg);
      onError?.(errorMsg);
      return;
    }

    if (!prompt.trim()) {
      const errorMsg = '请输入提示词';
      setError(errorMsg);
      onError?.(errorMsg);
      return;
    }

    try {
      setIsGenerating(true);
      setProgress(0);
      setError(null);
      setGeneratedImage(null);

      // Start generation
      const task = await generateImage({
        image_id: imageId,
        prompt: prompt.trim(),
        negative_prompt: negativePrompt.trim() || undefined,
        style: style !== 'default' ? style : undefined,
        strength,
        steps,
      });

      setTaskId(task.task_id);
      setTaskStatus(task.status);

      // Poll for status
      await pollTaskStatus(
        task.task_id,
        (updatedTask: GenerationTask) => {
          setTaskStatus(updatedTask.status);
          setTaskProgress(updatedTask.progress || 0);
          setProgress(updatedTask.progress || 0);
        },
        1000 // Poll every second
      );

      // Get final result
      const finalTask = await pollTaskStatus(task.task_id);
      if (finalTask.result_url) {
        setGeneratedImage(finalTask.result_url);
        onSuccess?.();
      }
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : '生成失败';
      setError(errorMsg);
      onError?.(errorMsg);
    } finally {
      setIsGenerating(false);
      setTaskId(null);
      setTaskStatus(null);
      setTaskProgress(0);
    }
  }, [
    imageId,
    prompt,
    negativePrompt,
    style,
    strength,
    steps,
    setIsGenerating,
    setGeneratedImage,
    setTaskId,
    setTaskStatus,
    setTaskProgress,
    setError,
    onSuccess,
    onError,
  ]);

  return {
    isGenerating: useEditorStore((state) => state.isGenerating),
    progress,
    generate,
  };
}
