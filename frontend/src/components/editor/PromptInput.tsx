import { useState } from 'react';
import { Sparkles, Wand2, Lightbulb, X } from 'lucide-react';
import { Textarea } from '@/components/ui/textarea';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { useEditorStore } from '@/stores/editorStore';
import { cn } from '@/utils/cn';

// Example prompts for inspiration
const EXAMPLE_PROMPTS = [
  '将背景换成梦幻的星空',
  '给人物添加金色光环效果',
  '转换成赛博朋克风格',
  '添加柔和的光影效果',
  '转换成水彩画风格',
  '给人物穿上古装汉服',
  '添加樱花飘落的场景',
  '转换成黑白电影风格',
];

interface PromptInputProps {
  className?: string;
}

export function PromptInput({ className }: PromptInputProps) {
  const { prompt, setPrompt, negativePrompt, setNegativePrompt } = useEditorStore();
  const [showExamples, setShowExamples] = useState(false);
  const [showNegative, setShowNegative] = useState(false);

  const handleExampleClick = (example: string) => {
    setPrompt(example);
    setShowExamples(false);
  };

  const charCount = prompt.length;
  const maxChars = 500;

  return (
    <div className={cn("space-y-4", className)}>
      {/* Main Prompt Input */}
      <div className="space-y-2">
        <div className="flex items-center justify-between">
          <label className="text-sm font-medium flex items-center gap-2">
            <Sparkles className="h-4 w-4 text-primary" />
            描述你想要的效果
          </label>
          <div className="flex items-center gap-2">
            <Button
              variant="ghost"
              size="sm"
              className="h-7 text-xs"
              onClick={() => setShowExamples(!showExamples)}
            >
              <Lightbulb className="h-3 w-3 mr-1" />
              灵感提示
            </Button>
            <span className={cn(
              "text-xs",
              charCount > maxChars ? "text-destructive" : "text-muted-foreground"
            )}>
              {charCount}/{maxChars}
            </span>
          </div>
        </div>

        <div className="relative">
          <Textarea
            value={prompt}
            onChange={(e) => setPrompt(e.target.value.slice(0, maxChars))}
            placeholder="例如：将背景换成梦幻的星空，给人物添加柔和的光影..."
            className="min-h-[120px] resize-none pr-10"
          />
          {prompt && (
            <Button
              variant="ghost"
              size="icon"
              className="absolute top-2 right-2 h-6 w-6"
              onClick={() => setPrompt('')}
            >
              <X className="h-3 w-3" />
            </Button>
          )}
        </div>

        {/* Example Prompts */}
        {showExamples && (
          <div className="p-3 rounded-lg bg-muted/50 space-y-2 animate-fade-in">
            <p className="text-xs text-muted-foreground">点击使用示例提示词：</p>
            <div className="flex flex-wrap gap-2">
              {EXAMPLE_PROMPTS.map((example, index) => (
                <Badge
                  key={index}
                  variant="secondary"
                  className="cursor-pointer hover:bg-primary hover:text-primary-foreground transition-colors"
                  onClick={() => handleExampleClick(example)}
                >
                  {example}
                </Badge>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Negative Prompt Toggle */}
      <div className="space-y-2">
        <Button
          variant="ghost"
          size="sm"
          className="h-7 text-xs text-muted-foreground"
          onClick={() => setShowNegative(!showNegative)}
        >
          <Wand2 className="h-3 w-3 mr-1" />
          {showNegative ? '隐藏' : '显示'}反向提示词（可选）
        </Button>

        {showNegative && (
          <div className="animate-fade-in">
            <Textarea
              value={negativePrompt}
              onChange={(e) => setNegativePrompt(e.target.value)}
              placeholder="描述你不想要的效果，例如：模糊、低质量、变形..."
              className="min-h-[80px] resize-none"
            />
            <p className="mt-1 text-xs text-muted-foreground">
              反向提示词可以帮助AI避免生成你不想要的内容
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
