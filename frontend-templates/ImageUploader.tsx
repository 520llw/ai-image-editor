// frontend/src/components/image/ImageUploader.tsx
import React, { useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, Image as ImageIcon } from 'lucide-react';
import { cn } from '@/lib/utils';

interface ImageUploaderProps {
  onUpload: (file: File) => void;
  previewUrl: string | null;
  isUploading: boolean;
}

export const ImageUploader: React.FC<ImageUploaderProps> = ({
  onUpload,
  previewUrl,
  isUploading,
}) => {
  const onDrop = useCallback(
    (acceptedFiles: File[]) => {
      if (acceptedFiles.length > 0) {
        onUpload(acceptedFiles[0]);
      }
    },
    [onUpload]
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/*': ['.png', '.jpg', '.jpeg', '.webp'],
    },
    maxFiles: 1,
    maxSize: 10 * 1024 * 1024, // 10MB
  });

  return (
    <div
      {...getRootProps()}
      className={cn(
        'relative border-2 border-dashed rounded-xl p-8 transition-all cursor-pointer',
        'hover:border-primary hover:bg-primary/5',
        isDragActive && 'border-primary bg-primary/10',
        previewUrl ? 'border-solid' : 'border-gray-300'
      )}
    >
      <input {...getInputProps()} />

      {previewUrl ? (
        <div className="relative">
          <img
            src={previewUrl}
            alt="Preview"
            className="w-full h-64 object-contain rounded-lg"
          />
          <div className="absolute inset-0 bg-black/50 flex items-center justify-center opacity-0 hover:opacity-100 transition-opacity rounded-lg">
            <p className="text-white flex items-center gap-2">
              <Upload className="w-5 h-5" />
              点击或拖拽更换图片
            </p>
          </div>
        </div>
      ) : (
        <div className="text-center">
          <div className="mx-auto w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mb-4">
            {isUploading ? (
              <div className="w-6 h-6 border-2 border-primary border-t-transparent rounded-full animate-spin" />
            ) : (
              <ImageIcon className="w-8 h-8 text-gray-400" />
            )}
          </div>
          <p className="text-lg font-medium text-gray-700 mb-1">
            {isDragActive ? '释放以上传图片' : '点击或拖拽上传图片'}
          </p>
          <p className="text-sm text-gray-500">
            支持 PNG, JPG, WEBP 格式，最大 10MB
          </p>
        </div>
      )}
    </div>
  );
};
