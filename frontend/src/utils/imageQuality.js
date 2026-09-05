// src/utils/imageQuality.js

export const checkImageQuality = (file) => {
  return new Promise((resolve) => {
    const img = new Image();
    img.onload = () => {
      const warnings = [];
      let isBlurry = false;
      let isTooDark = false;
      let brightnessValue = 0;
      let contrastValue = 0;
      
      // Check dimensions
      if (img.width < 400 || img.height < 400) {
        warnings.push(`Image resolution (${img.width}x${img.height}) is too low. Minimum 400x400 recommended.`);
      }
      
      // Check aspect ratio
      const aspectRatio = img.width / img.height;
      if (aspectRatio < 0.6 || aspectRatio > 1.8) {
        warnings.push(`Image aspect ratio (${aspectRatio.toFixed(2)}) is unusual. Documents typically have a 1.3-1.6 ratio.`);
      }
      
      // Check if image is too small
      if (img.width < 200 || img.height < 200) {
        warnings.push('Image is very small. Please upload a larger, clearer image.');
      }
      
      // Analyze image quality using canvas
      try {
        const canvas = document.createElement('canvas');
        canvas.width = Math.min(img.width, 800);
        canvas.height = Math.min(img.height, 800);
        const ctx = canvas.getContext('2d');
        ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
        const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
        const data = imageData.data;
        
        // Calculate brightness and contrast
        let sum = 0;
        let sumSquared = 0;
        let pixelCount = data.length / 4;
        
        for (let i = 0; i < data.length; i += 4) {
          const brightness = (data[i] + data[i+1] + data[i+2]) / 3;
          sum += brightness;
          sumSquared += brightness * brightness;
        }
        
        const mean = sum / pixelCount;
        const variance = (sumSquared / pixelCount) - (mean * mean);
        const stdDev = Math.sqrt(variance);
        
        brightnessValue = Math.round(mean);
        contrastValue = Math.round(stdDev);
        
        // Check brightness
        if (mean < 40) {
          warnings.push('Image is too dark. Please ensure good lighting when taking the photo.');
          isTooDark = true;
        } else if (mean > 220) {
          warnings.push('Image is overexposed (too bright). Please reduce brightness or adjust lighting.');
        } else if (mean < 80) {
          warnings.push('Image is quite dark. Better lighting would improve results.');
        }
        
        // Check contrast / blur
        if (stdDev < 20) {
          warnings.push('Image appears blurry or low contrast. Please ensure the document is in sharp focus.');
          isBlurry = true;
        } else if (stdDev < 35) {
          warnings.push('Image has low contrast. Please ensure the document is well-lit and in focus.');
        }
        
        console.log('Image analysis:', { 
          meanBrightness: brightnessValue, 
          contrast: contrastValue,
          width: img.width,
          height: img.height,
          aspectRatio: aspectRatio.toFixed(2),
          warnings: warnings.length
        });
        
      } catch (e) {
        console.log('Could not analyze image quality:', e);
      }
      
      resolve({
        width: img.width,
        height: img.height,
        warnings: warnings,
        isBlurry: isBlurry,
        isTooDark: isTooDark,
        passed: warnings.length === 0,
        details: {
          brightness: brightnessValue,
          contrast: contrastValue,
          aspectRatio: aspectRatio.toFixed(2)
        }
      });
    };
    
    img.onerror = () => {
      resolve({
        width: 0,
        height: 0,
        warnings: ['Could not load image. Please try another file.'],
        isBlurry: false,
        isTooDark: false,
        passed: false,
        details: {}
      });
    };
    
    img.src = URL.createObjectURL(file);
  });
};