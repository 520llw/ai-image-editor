import { useState, useRef, useCallback } from 'react';
import { Download, RefreshCw } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { cn } from '@/utils/cn';

interface ImageComparisonProps {
  originalImage: string;
  generatedImage: string;
  onRegenerate?: () => void;
  onDownload?: () => void;
  className?: string;
}

export function ImageComparison({
  originalImage,
  generatedImage,
  onRegenerate,
  onDownload,
  className,
}: ImageComparisonProps) {
  const [sliderPosition, setSliderPosition] = useState(50);
  const [isDragging, setIsDragging] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);

  const handleMove = useCallback(
    (clientX: number) => {
      if (!containerRef.current) return;
      
      const rect = containerRef.current.getBoundingClientRect();
      const x = clientX - rect.left;
      const percentage = Math.max(0, Math.min(100, (x / rect.width) * 100));
      setSliderPosition(percentage);
    },
    []
  );

  const handleMouseDown = useCallback(() => {
    setIsDragging(true);
  }, []);

  const handleMouseUp = useCallback(() => {
    setIsDragging(false);
  }, []);

  const handleMouseMove = useCallback(
    (e: React.MouseEvent) => {
      if (!isDragging) return;
      handleMove(e.clientX);
    },
    [isDragging, handleMove]
  );

  const handleTouchMove = useCallback(
    (e: React.TouchEvent) => {
      handleMove(e.touches[0].clientX);
    },
    [handleMove]
  );

  return (
    <div className={cn("space-y-4", className)}>
      {/* Labels */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Badge variant="secondary">原图</Badge>
          <Badge variant="default" className="bg-gradient-to-r from-violet-600 to-indigo-600">
            AI编辑后
          </Badge>
        </div>
        <div className="flex items-center gap-2">
          {onRegenerate && (
            <Button
              variant="outline"
              size="sm"
              onClick={onRegenerate}
            >
              <RefreshCw className="h-4 w-4 mr-2" />
              重新生成
            </Button>
          )}
          {onDownload && (
            <Button
              variant="default"
              size="sm"
              onClick={onDownload}
              className="bg-gradient-to-r from-violet-600 to-indigo-600"
            >
              <Download className="h-4 w-4 mr-2" />
              下载
            </Button>
          )}
        </div>
      </div>

      {/* Comparison Container */}
      <div
        ref={containerRef}
        className="relative select-none overflow-hidden rounded-xl cursor-ew-resize"
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        onMouseLeave={handleMouseUp}
        onTouchMove={handleTouchMove}
        onTouchEnd={handleMouseUp}
      >
        {/* Generated Image (Background) */}
        <div className="relative aspect-video bg-muted">
          <img
            src={generatedImage}
            alt="Generated"
            className="absolute inset-0 w-full h-full object-contain"
            draggable={false}
          />
        </div>

        {/* Original Image (Foreground with clip) */}
        <div
          className="absolute inset-0 overflow-hidden"
          style={{ clipPath: `inset(0 ${100 - sliderPosition}% 0 0)` }}
        >
          <div className="relative aspect-video bg-muted">
            <img
              src={originalImage}
              alt="Original"
              className="absolute inset-0 w-full h-full object-contain"
              draggable={false}
            />
          </div>
        </div>

        {/* Slider Handle */}
        <div
          className="absolute top-0 bottom-0 w-1 bg-white cursor-ew-resize shadow-lg"
          style={{ left: `${sliderPosition}%`, transform: 'translateX(-50%)' }}
          onMouseDown={handleMouseDown}
          onTouchStart={handleMouseDown}
        >
          {/* Handle Circle */}
          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-8 h-8 bg-white rounded-full shadow-lg flex items-center justify-center">
            <div className="flex gap-0.5">
              <div className="w-0.5 h-3 bg-gray-400 rounded-full" />
              <div className="w-0.5 h-3 bg-gray-400 rounded-full" />
            </div>
          </div>
        </div>

        {/* Labels on images */}
        <div 
          className="absolute bottom-4 left-4 px-3 py-1.5 rounded-full bg-black/50 text-white text-xs font-medium"
          style={{ opacity: sliderPosition > 20 ? 1 : 0 }}
        >
          原图
        </div>
        <div 
          className="absolute bottom-4 right-4 px-3 py-1.5 rounded-full bg-violet-600/80 text-white text-xs font-medium"
          style={{ opacity: sliderPosition < 80 ? 1 : 0 }}
        >
          AI编辑
        </div>
      </div>

      {/* Hint */}
      <p className="text-center text-xs text-muted-foreground">
        拖动滑块对比原图和编辑后的效果
      </p>
    </div>
  );
}
