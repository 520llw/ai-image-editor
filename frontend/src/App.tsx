import { useCallback } from 'react';
import { Header } from '@/components/layout/Header';
import { ImageUploader } from '@/components/image/ImageUploader';
import { ImagePreview } from '@/components/image/ImagePreview';
import { ImageComparison } from '@/components/image/ImageComparison';
import { PromptInput } from '@/components/editor/PromptInput';
import { StyleSelector } from '@/components/editor/StyleSelector';
import { StrengthSlider } from '@/components/editor/StrengthSlider';
import { StepsSlider } from '@/components/editor/StepsSlider';
import { GenerateButton } from '@/components/editor/GenerateButton';
import { Toaster, toast } from '@/components/ui/use-toast';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';
import { useEditorStore } from '@/stores/editorStore';
import { useImageGeneration } from '@/hooks/useImageGeneration';
import { getImageDownloadUrl } from '@/api/imageApi';
import { Sparkles, Image as ImageIcon, Settings2, Download, AlertCircle } from 'lucide-react';

function App() {
  const {
    originalImage,
    generatedImage,
    imageId,
    error,
    setError,
    reset,
  } = useEditorStore();

  const handleError = useCallback((message: string) => {
    toast({
      variant: 'destructive',
      title: '出错了',
      description: message,
    });
  }, []);

  const handleSuccess = useCallback(() => {
    toast({
      variant: 'success',
      title: '生成成功',
      description: '图片已生成完成，可以下载保存',
    });
  }, []);

  const { generate } = useImageGeneration(handleSuccess, handleError);

  const handleDownload = useCallback(() => {
    if (generatedImage) {
      const link = document.createElement('a');
      link.href = generatedImage;
      link.download = `ai-edited-${Date.now()}.png`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      
      toast({
        variant: 'success',
        title: '下载开始',
        description: '图片正在下载中...',
      });
    }
  }, [generatedImage]);

  const handleReset = useCallback(() => {
    reset();
    toast({
      title: '已重置',
      description: '所有设置已恢复到默认状态',
    });
  }, [reset]);

  return (
    <div className="min-h-screen bg-background">
      <Toaster />
      <Header />

      <main className="container py-8">
        {/* Hero Section */}
        <div className="text-center mb-10 space-y-4">
          <h1 className="text-4xl md:text-5xl font-bold bg-gradient-to-r from-violet-400 via-purple-400 to-indigo-400 bg-clip-text text-transparent">
            AI 智能图片编辑器
          </h1>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            上传图片，用自然语言描述你想要的效果，AI 将为你创造惊艳的视觉作品
          </p>
          <div className="flex items-center justify-center gap-2">
            <Badge variant="secondary" className="text-xs">
              <Sparkles className="h-3 w-3 mr-1" />
              基于 Stable Diffusion
            </Badge>
            <Badge variant="secondary" className="text-xs">
              免费使用
            </Badge>
            <Badge variant="secondary" className="text-xs">
              无需注册
            </Badge>
          </div>
        </div>

        {/* Error Alert */}
        {error && (
          <Alert variant="destructive" className="mb-6">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {/* Main Content */}
        <div className="grid lg:grid-cols-2 gap-8">
          {/* Left Column - Image Upload & Preview */}
          <div className="space-y-6">
            <Card className="border-border/50">
              <CardHeader className="pb-4">
                <CardTitle className="text-lg flex items-center gap-2">
                  <ImageIcon className="h-5 w-5 text-primary" />
                  图片上传
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ImageUploader onError={handleError} />
              </CardContent>
            </Card>

            {/* Original Image Preview */}
            {originalImage && (
              <Card className="border-border/50 animate-slide-up">
                <CardHeader className="pb-4">
                  <CardTitle className="text-lg flex items-center gap-2">
                    <ImageIcon className="h-5 w-5 text-primary" />
                    原图预览
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <ImagePreview
                    src={originalImage}
                    alt="Original"
                    showControls={true}
                  />
                </CardContent>
              </Card>
            )}
          </div>

          {/* Right Column - Editor Controls */}
          <div className="space-y-6">
            <Card className="border-border/50">
              <CardHeader className="pb-4">
                <CardTitle className="text-lg flex items-center gap-2">
                  <Settings2 className="h-5 w-5 text-primary" />
                  编辑设置
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                <PromptInput />
                <div className="h-px bg-border" />
                <StyleSelector />
                <div className="h-px bg-border" />
                <StrengthSlider />
                <div className="h-px bg-border" />
                <StepsSlider />
              </CardContent>
            </Card>

            {/* Generate Button */}
            <GenerateButton onGenerate={generate} />

            {/* Reset Button */}
            {(originalImage || generatedImage) && (
              <button
                onClick={handleReset}
                className="w-full text-sm text-muted-foreground hover:text-foreground transition-colors"
              >
                重置所有内容
              </button>
            )}
          </div>
        </div>

        {/* Result Section */}
        {generatedImage && originalImage && (
          <div className="mt-10 animate-slide-up">
            <Card className="border-border/50">
              <CardHeader className="pb-4">
                <CardTitle className="text-lg flex items-center gap-2">
                  <Sparkles className="h-5 w-5 text-primary" />
                  生成结果
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ImageComparison
                  originalImage={originalImage}
                  generatedImage={generatedImage}
                  onRegenerate={generate}
                  onDownload={handleDownload}
                />
              </CardContent>
            </Card>
          </div>
        )}

        {/* Generated Image Only (if no original for comparison) */}
        {generatedImage && !originalImage && (
          <div className="mt-10 animate-slide-up">
            <Card className="border-border/50">
              <CardHeader className="pb-4">
                <CardTitle className="text-lg flex items-center gap-2">
                  <Sparkles className="h-5 w-5 text-primary" />
                  生成结果
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <ImagePreview
                  src={generatedImage}
                  alt="Generated"
                  showControls={true}
                  onDownload={handleDownload}
                />
                <div className="flex justify-center gap-2">
                  <button
                    onClick={generate}
                    className="text-sm text-muted-foreground hover:text-foreground transition-colors"
                  >
                    重新生成
                  </button>
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Features Section */}
        <div className="mt-16 grid md:grid-cols-3 gap-6">
          <div className="p-6 rounded-xl bg-card border border-border/50 text-center space-y-3">
            <div className="h-12 w-12 mx-auto rounded-xl bg-primary/10 flex items-center justify-center">
              <Sparkles className="h-6 w-6 text-primary" />
            </div>
            <h3 className="font-semibold">AI 智能编辑</h3>
            <p className="text-sm text-muted-foreground">
              使用先进的 AI 模型，根据你的描述智能编辑图片
            </p>
          </div>
          <div className="p-6 rounded-xl bg-card border border-border/50 text-center space-y-3">
            <div className="h-12 w-12 mx-auto rounded-xl bg-primary/10 flex items-center justify-center">
              <ImageIcon className="h-6 w-6 text-primary" />
            </div>
            <h3 className="font-semibold">多种风格</h3>
            <p className="text-sm text-muted-foreground">
              支持赛博朋克、水彩画、油画等多种艺术风格
            </p>
          </div>
          <div className="p-6 rounded-xl bg-card border border-border/50 text-center space-y-3">
            <div className="h-12 w-12 mx-auto rounded-xl bg-primary/10 flex items-center justify-center">
              <Download className="h-6 w-6 text-primary" />
            </div>
            <h3 className="font-semibold">高清下载</h3>
            <p className="text-sm text-muted-foreground">
              生成高质量图片，支持一键下载保存
            </p>
          </div>
        </div>

        {/* Footer */}
        <footer className="mt-16 pt-8 border-t border-border/50 text-center text-sm text-muted-foreground">
          <p>© 2024 AI Image Editor. All rights reserved.</p>
          <p className="mt-2">
            Powered by Stable Diffusion · Built with React & FastAPI
          </p>
        </footer>
      </main>
    </div>
  );
}

export default App;
