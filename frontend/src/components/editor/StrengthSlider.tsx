import { SlidersHorizontal } from 'lucide-react';
import { Slider } from '@/components/ui/slider';
import { useEditorStore } from '@/stores/editorStore';

export function StrengthSlider() {
  const { strength, setStrength } = useEditorStore();

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <label className="text-sm font-medium flex items-center gap-2">
          <SlidersHorizontal className="h-4 w-4 text-primary" />
          编辑强度
        </label>
        <span className="text-sm font-medium text-primary">
          {Math.round(strength * 100)}%
        </span>
      </div>

      <Slider
        value={[strength * 100]}
        onValueChange={(value) => setStrength(value[0] / 100)}
        min={10}
        max={100}
        step={5}
        className="w-full"
      />

      <div className="flex justify-between text-xs text-muted-foreground">
        <span>保守（保留更多原图特征）</span>
        <span>激进（更大程度改变）</span>
      </div>

      <p className="text-xs text-muted-foreground">
        当前设置：{strength < 0.4 ? '保守' : strength < 0.7 ? '平衡' : '激进'}模式
        {strength < 0.4 && ' - 保留更多原图细节和特征'}
        {strength >= 0.4 && strength < 0.7 && ' - 在保持原图基础上进行适度编辑'}
        {strength >= 0.7 && ' - 允许AI进行大幅度创意编辑'}
      </p>
    </div>
  );
}
