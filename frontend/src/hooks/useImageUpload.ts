import { useState, useCallback } from 'react';
import { uploadImage, validateImageFile, createImagePreview } from '@/api/imageApi';
import { useEditorStore } from '@/stores/editorStore';

interface UseImageUploadReturn {
  isDragging: boolean;
  uploadProgress: number;
  handleDragEnter: (e: React.DragEvent) => void;
  handleDragLeave: (e: React.DragEvent) => void;
  handleDragOver: (e: React.DragEvent) => void;
  handleDrop: (e: React.DragEvent) => Promise<void>;
  handleFileSelect: (e: React.ChangeEvent<HTMLInputElement>) => Promise<void>;
}

export function useImageUpload(onError?: (error: string) => void): UseImageUploadReturn {
  const [isDragging, setIsDragging] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  
  const { 
    setIsUploading, 
    setOriginalImage, 
    setImageId,
    setError 
  } = useEditorStore();

  const processFile = useCallback(async (file: File) => {
    // Validate file
    const validation = validateImageFile(file);
    if (!validation.valid) {
      const errorMsg = validation.error || '文件验证失败';
      setError(errorMsg);
      onError?.(errorMsg);
      return;
    }

    try {
      setIsUploading(true);
      setUploadProgress(0);
      setError(null);

      // Create preview first
      const preview = await createImagePreview(file);
      setOriginalImage(preview);

      // Upload file
      const response = await uploadImage(file, (progress) => {
        setUploadProgress(progress);
      });

      setImageId(response.image_id);
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : '上传失败';
      setError(errorMsg);
      onError?.(errorMsg);
      setOriginalImage(null);
    } finally {
      setIsUploading(false);
    }
  }, [setIsUploading, setOriginalImage, setImageId, setError, onError]);

  const handleDragEnter = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  }, []);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
  }, []);

  const handleDrop = useCallback(async (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);

    const files = e.dataTransfer.files;
    if (files.length > 0) {
      await processFile(files[0]);
    }
  }, [processFile]);

  const handleFileSelect = useCallback(async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      await processFile(files[0]);
    }
    // Reset input
    e.target.value = '';
  }, [processFile]);

  return {
    isDragging,
    uploadProgress,
    handleDragEnter,
    handleDragLeave,
    handleDragOver,
    handleDrop,
    handleFileSelect,
  };
}
