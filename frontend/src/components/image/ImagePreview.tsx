import { useState } from 'react';
import { ZoomIn, ZoomOut, RotateCcw, Download, X } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { cn } from '@/utils/cn';

interface ImagePreviewProps {
  src: string;
  alt: string;
  onClose?: () => void;
  onDownload?: () => void;
  className?: string;
  showControls?: boolean;
}

export function ImagePreview({ 
  src, 
  alt, 
  onClose, 
  onDownload,
  className,
  showControls = true 
}: ImagePreviewProps) {
  const [scale, setScale] = useState(1);
  const [isLoading, setIsLoading] = useState(true);

  const handleZoomIn = () => {
    setScale(prev => Math.min(prev + 0.25, 3));
  };

  const handleZoomOut = () => {
    setScale(prev => Math.max(prev - 0.25, 0.5));
  };

  const handleReset = () => {
    setScale(1);
  };

  return (
    <div className={cn("relative rounded-lg overflow-hidden bg-muted", className)}>
      {/* Loading state */}
      {isLoading && (
        <div className="absolute inset-0 flex items-center justify-center bg-muted">
          <div className="loading-shimmer absolute inset-0" />
          <div className="relative z-10 flex flex-col items-center gap-2">
            <div className="h-8 w-8 border-2 border-primary border-t-transparent rounded-full animate-spin" />
            <span className="text-sm text-muted-foreground">加载中...</span>
          </div>
        </div>
      )}

      {/* Image */}
      <div 
        className="overflow-auto max-h-[600px] flex items-center justify-center"
        style={{ minHeight: '300px' }}
      >
        <img
          src={src}
          alt={alt}
          className="transition-transform duration-200"
          style={{ 
            transform: `scale(${scale})`,
            maxWidth: '100%',
            height: 'auto',
          }}
          onLoad={() => setIsLoading(false)}
        />
      </div>

      {/* Controls */}
      {showControls && !isLoading && (
        <div className="absolute bottom-4 left-1/2 -translate-x-1/2 flex items-center gap-2 p-2 rounded-full glass">
          <Button
            variant="ghost"
            size="icon"
            className="h-8 w-8"
            onClick={handleZoomOut}
            disabled={scale <= 0.5}
          >
            <ZoomOut className="h-4 w-4" />
          </Button>
          <span className="text-xs font-medium min-w-[50px] text-center">
            {Math.round(scale * 100)}%
          </span>
          <Button
            variant="ghost"
            size="icon"
            className="h-8 w-8"
            onClick={handleZoomIn}
            disabled={scale >= 3}
          >
            <ZoomIn className="h-4 w-4" />
          </Button>
          <div className="w-px h-4 bg-border mx-1" />
          <Button
            variant="ghost"
            size="icon"
            className="h-8 w-8"
            onClick={handleReset}
          >
            <RotateCcw className="h-4 w-4" />
          </Button>
          {onDownload && (
            <>
              <div className="w-px h-4 bg-border mx-1" />
              <Button
                variant="ghost"
                size="icon"
                className="h-8 w-8"
                onClick={onDownload}
              >
                <Download className="h-4 w-4" />
              </Button>
            </>
          )}
        </div>
      )}

      {/* Close button */}
      {onClose && (
        <Button
          variant="ghost"
          size="icon"
          className="absolute top-2 right-2 h-8 w-8 rounded-full bg-background/80"
          onClick={onClose}
        >
          <X className="h-4 w-4" />
        </Button>
      )}
    </div>
  );
}
