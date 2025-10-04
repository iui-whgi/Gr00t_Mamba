# SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

import os
import torch
from torch import nn
from transformers import MambaForCausalLM, AutoTokenizer
from transformers.feature_extraction_utils import BatchFeature

class MambaBackbone(nn.Module):
    def __init__(
        self,
        tune_llm: bool = False,
        tune_visual: bool = False,  # Mamba는 텍스트 전용이므로 무시
        select_layer: int = -1,
        reproject_vision: bool = False,
        use_flash_attention: bool = False,
        load_bf16: bool = False,
        mamba_path: str | None = None,
        project_to_dim: int = 1536,
        mamba_type: str = "mamba-2.8b",
    ):
        super().__init__()
        
        # Mamba 모델 로드
        if mamba_path:
            self.mamba_model = MambaForCausalLM.from_pretrained(mamba_path)
            self.tokenizer = AutoTokenizer.from_pretrained(mamba_path)
        else:
            model_name = f"state-spaces/{mamba_type}-hf"
            self.mamba_model = MambaForCausalLM.from_pretrained(model_name)
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        
        # 프로젝션 레이어
        if project_to_dim is not None:
            self.mamba_linear = torch.nn.Linear(self.mamba_model.config.hidden_size, project_to_dim)
        else:
            self.mamba_linear = torch.nn.Identity()
        
        self.select_layer = select_layer
        self.set_trainable_parameters(tune_llm, tune_visual)
    
    def set_trainable_parameters(self, tune_llm: bool, tune_visual: bool):
        self.tune_llm = tune_llm
        self.tune_visual = tune_visual  # Mamba는 비전 없음
        
        for p in self.parameters():
            p.requires_grad = True
            
        if not tune_llm:
            self.mamba_model.requires_grad_(False)
        
        print(f"Tune backbone llm: {self.tune_llm}")
        print(f"Tune backbone visual: {self.tune_visual} (Mamba는 텍스트 전용)")
    
    def prepare_input(self, batch: dict) -> BatchFeature:
        return BatchFeature(data=batch)
    
    def forward_mamba(self, vl_input: BatchFeature):
        # Eagle과 동일한 인터페이스 유지
        mamba_prefix = "eagle_"  # 기존 키 유지
        mamba_input = {
            k.removeprefix(mamba_prefix): v
            for k, v in vl_input.items()
            if k.startswith(mamba_prefix)
        }
        
        # 텍스트 입력 처리
        if "input_ids" in mamba_input:
            input_ids = mamba_input["input_ids"]
            attention_mask = mamba_input.get("attention_mask", None)
            
            # Mamba 모델 실행
            outputs = self.mamba_model(
                input_ids=input_ids,
                attention_mask=attention_mask,
                output_hidden_states=True,
                return_dict=True
            )
            
            # 선택된 레이어의 특징 추출
            mamba_features = outputs.hidden_states[self.select_layer]
            mamba_features = self.mamba_linear(mamba_features)
            
            return mamba_features, attention_mask
        else:
            # 비전 입력이 있는 경우 처리 (필요시)
            raise NotImplementedError("Mamba는 현재 텍스트 전용입니다")
    
    def forward(self, vl_input: BatchFeature) -> BatchFeature:
        mamba_embeds, mamba_mask = self.forward_mamba(vl_input)
        
        return BatchFeature(
            data={"backbone_features": mamba_embeds, "backbone_attention_mask": mamba_mask}
        )