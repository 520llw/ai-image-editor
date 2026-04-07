import { Cpu } from 'lucide-react';
import { Slider } from '@/components/ui/slider';
import { useEditorStore } from '@/stores/editorStore';

export function StepsSlider() {
  const { steps, setSteps } = useEditorStore();

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <label className="text-sm font-medium flex items-center gap-2">
          <Cpu className="h-4 w-4 text-primary" />
          推理步数
        </label>
        <span className="text-sm font-medium text-primary">
          {steps} 步
        </span>
      </div>

      <Slider
        value={[steps]}
        onValueChange={(value) => setSteps(value[0])}
        min={10}
        max={50}
        step={5}
        className="w-full"
      />

      <div className="flex justify-between text-xs text-muted-foreground">
        <span>快速（10步）</span>
        <span>高质量（50步）</span>
      </div>

      <p className="text-xs text-muted-foreground">
        步数越多，生成质量越高，但耗时也更长
        {steps <= 20 && ' - 适合快速预览'}
        {steps > 20 && steps <= 35 && ' - 平衡质量与速度'}
        {steps > 35 && ' - 追求最佳质量'}
      </p>
    </div>
  );
}
