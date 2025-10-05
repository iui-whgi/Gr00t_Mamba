#!/usr/bin/env python3
"""
AutoModel을 사용하여 iui-whgi/gr00t-60dataset-10k 모델을 로드하는 스크립트
"""

from transformers import AutoModel, AutoTokenizer
import torch

def load_gr00t_model():
    """iui-whgi/gr00t-60dataset-10k 모델을 로드합니다."""
    
    model_name = "iui-whgi/gr00t-60dataset-10k"
    
    print(f"모델 로딩 시작: {model_name}")
    
    try:
        # 토크나이저 로드
        print("토크나이저 로딩 중...")
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        print("토크나이저 로딩 완료!")
        
        # 모델 로드
        print("모델 로딩 중...")
        model = AutoModel.from_pretrained(model_name)
        print("모델 로딩 완료!")
        
        # 모델 정보 출력
        print(f"\n모델 정보:")
        print(f"- 모델 이름: {model_name}")
        print(f"- 모델 타입: {type(model).__name__}")
        print(f"- 모델 파라미터 수: {sum(p.numel() for p in model.parameters()):,}")
        print(f"- 토크나이저 vocab 크기: {tokenizer.vocab_size}")
        
        # 간단한 테스트
        print(f"\n모델 테스트:")
        test_text = "Hello, this is a test sentence."
        inputs = tokenizer(test_text, return_tensors="pt")
        
        with torch.no_grad():
            outputs = model(**inputs)
            print(f"- 입력 텍스트: {test_text}")
            print(f"- 출력 shape: {outputs.last_hidden_state.shape}")
        
        return model, tokenizer
        
    except Exception as e:
        print(f"모델 로딩 중 오류 발생: {e}")
        return None, None

if __name__ == "__main__":
    model, tokenizer = load_gr00t_model()
    
    if model is not None and tokenizer is not None:
        print("\n✅ 모델 로딩 성공!")
    else:
        print("\n❌ 모델 로딩 실패!")

