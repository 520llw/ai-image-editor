import { Wand2, Loader2, Sparkles } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { useEditorStore } from '@/stores/editorStore';
import { cn } from '@/utils/cn';

interface GenerateButtonProps {
  onGenerate: () => void;
  className?: string;
}

export function GenerateButton({ onGenerate, className }: GenerateButtonProps) {
  const { 
    isGenerating, 
    taskProgress, 
    prompt, 
    imageId,
    taskStatus 
  } = useEditorStore();

  const canGenerate = prompt.trim().length > 0 && imageId !== null;

  // Get status text
  const getStatusText = () => {
    if (!isGenerating) return '';
    switch (taskStatus) {
      case 'pending':
        return '等待中...';
      case 'processing':
        return `生成中... ${taskProgress}%`;
      default:
        return '处理中...';
    }
  };

  return (
    <div className={cn("space-y-3", className)}>
      {/* Progress */}
      {isGenerating && (
        <div className="space-y-2">
          <Progress value={taskProgress} className="h-2" />
          <p className="text-center text-sm text-muted-foreground">
            {getStatusText()}
          </p>
        </div>
      )}

      {/* Generate Button */}
      <Button
        onClick={onGenerate}
        disabled={!canGenerate || isGenerating}
        size="lg"
        className={cn(
          "w-full h-14 text-lg font-semibold relative overflow-hidden",
          "bg-gradient-to-r from-violet-600 via-purple-600 to-indigo-600",
          "hover:from-violet-700 hover:via-purple-700 hover:to-indigo-700",
          "transition-all duration-300",
          !canGenerate && "opacity-50 cursor-not-allowed",
          isGenerating && "animate-pulse-glow"
        )}
      >
        {/* Background animation */}
        <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/10 to-transparent translate-x-[-100%] animate-[shimmer_2s_infinite]" />
        
        {/* Content */}
        <span className="relative z-10 flex items-center justify-center gap-2">
          {isGenerating ? (
            <>
              <Loader2 className="h-5 w-5 animate-spin" />
              生成中...
            </>
          ) : (
            <>
              <Sparkles className="h-5 w-5" />
              {canGenerate ? '开始AI编辑' : '请先上传图片并输入提示词'}
            </>
          )}
        </span>
      </Button>

      {/* Hint */}
      {!canGenerate && !isGenerating && (
        <p className="text-center text-xs text-muted-foreground">
          {!imageId && '请先上传一张图片'}
          {imageId && !prompt.trim() && '请输入描述编辑效果的提示词'}
        </p>
      )}
    </div>
  );
}
