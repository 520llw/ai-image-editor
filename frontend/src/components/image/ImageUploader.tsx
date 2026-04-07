import { useRef } from 'react';
import { Upload, Image as ImageIcon, Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { useImageUpload } from '@/hooks/useImageUpload';
import { useEditorStore } from '@/stores/editorStore';
import { cn } from '@/utils/cn';

interface ImageUploaderProps {
  onError?: (error: string) => void;
}

export function ImageUploader({ onError }: ImageUploaderProps) {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const { 
    isDragging, 
    uploadProgress, 
    handleDragEnter, 
    handleDragLeave, 
    handleDragOver, 
    handleDrop, 
    handleFileSelect 
  } = useImageUpload(onError);
  
  const { isUploading, originalImage } = useEditorStore();

  const handleClick = () => {
    fileInputRef.current?.click();
  };

  // If already has image, show smaller uploader
  if (originalImage) {
    return (
      <div className="flex items-center gap-4 p-4 rounded-lg border border-border bg-card/50">
        <div className="flex items-center gap-3 flex-1">
          <div className="h-12 w-12 rounded-lg overflow-hidden bg-muted">
            <img 
              src={originalImage} 
              alt="Uploaded" 
              className="h-full w-full object-cover"
            />
          </div>
          <div className="flex flex-col">
            <span className="text-sm font-medium">图片已上传</span>
            <span className="text-xs text-muted-foreground">
              点击更换图片
            </span>
          </div>
        </div>
        <Button
          variant="outline"
          size="sm"
          onClick={handleClick}
          disabled={isUploading}
        >
          {isUploading ? (
            <Loader2 className="h-4 w-4 animate-spin" />
          ) : (
            <Upload className="h-4 w-4 mr-2" />
          )}
          更换
        </Button>
        <input
          ref={fileInputRef}
          type="file"
          accept="image/jpeg,image/jpg,image/png,image/webp"
          onChange={handleFileSelect}
          className="hidden"
        />
      </div>
    );
  }

  return (
    <div
      onClick={handleClick}
      onDragEnter={handleDragEnter}
      onDragLeave={handleDragLeave}
      onDragOver={handleDragOver}
      onDrop={handleDrop}
      className={cn(
        "relative group cursor-pointer rounded-xl border-2 border-dashed transition-all duration-300",
        "min-h-[300px] flex flex-col items-center justify-center p-8",
        isDragging 
          ? "border-primary bg-primary/5 scale-[1.02]" 
          : "border-muted-foreground/25 hover:border-muted-foreground/50 hover:bg-muted/50",
        isUploading && "pointer-events-none opacity-70"
      )}
    >
      <input
        ref={fileInputRef}
        type="file"
        accept="image/jpeg,image/jpg,image/png,image/webp"
        onChange={handleFileSelect}
        className="hidden"
      />

      {/* Background decoration */}
      <div className="absolute inset-0 overflow-hidden rounded-xl">
        <div className="absolute -top-20 -right-20 w-40 h-40 bg-violet-500/10 rounded-full blur-3xl" />
        <div className="absolute -bottom-20 -left-20 w-40 h-40 bg-indigo-500/10 rounded-full blur-3xl" />
      </div>

      {/* Content */}
      <div className="relative z-10 flex flex-col items-center text-center space-y-4">
        {/* Icon */}
        <div className={cn(
          "h-20 w-20 rounded-2xl flex items-center justify-center transition-all duration-300",
          "bg-gradient-to-br from-violet-500/20 to-indigo-500/20",
          isDragging && "scale-110 from-violet-500/30 to-indigo-500/30"
        )}>
          {isUploading ? (
            <Loader2 className="h-10 w-10 text-primary animate-spin" />
          ) : (
            <ImageIcon className={cn(
              "h-10 w-10 text-primary transition-transform duration-300",
              isDragging && "scale-110"
            )} />
          )}
        </div>

        {/* Text */}
        <div className="space-y-2">
          <h3 className="text-lg font-semibold">
            {isUploading ? '上传中...' : '拖拽或点击上传图片'}
          </h3>
          <p className="text-sm text-muted-foreground max-w-sm">
            支持 JPG、PNG、WebP 格式，文件大小不超过 10MB
          </p>
        </div>

        {/* Upload Button */}
        {!isUploading && (
          <Button 
            variant="outline" 
            className="mt-4"
            onClick={(e) => {
              e.stopPropagation();
              handleClick();
            }}
          >
            <Upload className="h-4 w-4 mr-2" />
            选择文件
          </Button>
        )}

        {/* Progress */}
        {isUploading && (
          <div className="w-full max-w-xs space-y-2">
            <Progress value={uploadProgress} className="h-2" />
            <p className="text-xs text-muted-foreground">
              {uploadProgress}%
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
