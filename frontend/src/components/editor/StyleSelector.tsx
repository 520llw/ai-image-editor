import { Palette } from 'lucide-react';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { useEditorStore } from '@/stores/editorStore';
import type { StyleOption } from '@/types';

const STYLE_OPTIONS: StyleOption[] = [
  { id: 'default', name: '默认风格', description: '保持原图风格，根据提示词进行编辑' },
  { id: 'cyberpunk', name: '赛博朋克', description: '霓虹灯光、科技感、未来主义风格' },
  { id: 'watercolor', name: '水彩画', description: '柔和的水彩笔触和艺术效果' },
  { id: 'oil-painting', name: '油画', description: '经典的油画质感和笔触' },
  { id: 'sketch', name: '素描', description: '黑白素描线条风格' },
  { id: 'anime', name: '动漫', description: '日式动漫卡通风格' },
  { id: 'pixel-art', name: '像素艺术', description: '复古像素游戏风格' },
  { id: '3d-render', name: '3D渲染', description: '逼真的3D渲染效果' },
  { id: 'vintage', name: '复古', description: '怀旧复古色调和质感' },
  { id: 'fantasy', name: '奇幻', description: '魔幻奇幻艺术风格' },
];

export function StyleSelector() {
  const { style, setStyle } = useEditorStore();

  const selectedStyle = STYLE_OPTIONS.find(s => s.id === style);

  return (
    <div className="space-y-2">
      <label className="text-sm font-medium flex items-center gap-2">
        <Palette className="h-4 w-4 text-primary" />
        艺术风格
      </label>
      
      <Select value={style} onValueChange={setStyle}>
        <SelectTrigger className="w-full">
          <SelectValue placeholder="选择风格" />
        </SelectTrigger>
        <SelectContent>
          {STYLE_OPTIONS.map((option) => (
            <SelectItem key={option.id} value={option.id}>
              <div className="flex flex-col items-start">
                <span className="font-medium">{option.name}</span>
                <span className="text-xs text-muted-foreground">
                  {option.description}
                </span>
              </div>
            </SelectItem>
          ))}
        </SelectContent>
      </Select>

      {selectedStyle && selectedStyle.id !== 'default' && (
        <p className="text-xs text-muted-foreground">
          已选择：{selectedStyle.name} - {selectedStyle.description}
        </p>
      )}
    </div>
  );
}
