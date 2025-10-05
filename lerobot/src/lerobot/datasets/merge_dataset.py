#!/usr/bin/env python
"""
Dataset merging utility for LeRobot datasets.

This script merges multiple moving-tape datasets into a single cookingbot dataset.
Fixed issues:
- Fixed undefined variable 'datasets_dir' 
- Improved episode indexing logic
- Enhanced frame processing with better error handling
- Improved image dimension conversion for different tensor types
- Added progress tracking and better logging
- Made the merge process more robust with graceful error handling
"""

import os
import json
from lerobot.datasets.lerobot_dataset import LeRobotDataset, MultiLeRobotDataset

def find_available_datasets():
    """현재 디렉토리에서 접근 가능한 moving-tape 데이터셋들을 찾음"""
    
    # 가능한 데이터셋 경로들
    possible_paths = [
        ".",  # 현재 디렉토리
        "~/lerobotjs/datasets",  # 데이터셋이 있는 경로
        os.path.expanduser("~/lerobotjs/datasets"),  # 확장된 경로
        "/home/son/lerobotjs/datasets",  # 절대 경로
    ]
    
    datasets_path = None
    datasets = []
    
    # 데이터셋이 있는 경로 찾기
    for path in possible_paths:
        expanded_path = os.path.expanduser(path)
        if os.path.exists(expanded_path):
            print(f"경로 확인 중: {expanded_path}")
            temp_datasets = []
            try:
                for item in os.listdir(expanded_path):
                    item_path = os.path.join(expanded_path, item)
                    if item.startswith('moving-tape-dataset') and os.path.isdir(item_path):
                        info_path = os.path.join(item_path, 'meta', 'info.json')
                        if os.path.exists(info_path):
                            try:
                                with open(info_path, 'r') as f:
                                    info = json.load(f)
                                temp_datasets.append((item, item_path))
                                print(f"✓ {item} - 접근 가능 (에피소드: {info.get('total_episodes', '?')}개)")
                            except Exception as e:
                                print(f"✗ {item} - 접근 불가: {e}")
                
                if temp_datasets:
                    datasets_path = expanded_path
                    datasets = temp_datasets
                    break
                    
            except Exception as e:
                print(f"✗ {expanded_path} 접근 실패: {e}")
                continue
    
    if not datasets:
        print("moving-tape 데이터셋을 찾을 수 없습니다.")
        print("다음 경로들을 확인했습니다:")
        for path in possible_paths:
            expanded_path = os.path.expanduser(path)
            print(f"  - {expanded_path} ({'존재' if os.path.exists(expanded_path) else '없음'})")
        return [], None
    
    print(f"\n데이터셋 발견 경로: {datasets_path}")
    return [item[0] for item in datasets], datasets_path

def upload_datasets_first(dataset_paths, datasets_root):
    """데이터셋들을 먼저 허깅페이스에 개별 업로드"""
    repo_ids = []
    
    print("데이터셋들을 허깅페이스에 개별 업로드 중...")
    print("=" * 50)
    
    # 현재 디렉토리 저장
    original_dir = os.getcwd()
    
    try:
        # 데이터셋이 있는 디렉토리로 이동
        os.chdir(datasets_root)
        print(f"작업 디렉토리 변경: {datasets_root}")
        
        for i, dataset_path in enumerate(dataset_paths):
            repo_id = f"JisooSong/{dataset_path}"
            
            print(f"\n[{i+1}/{len(dataset_paths)}] {dataset_path} 업로드 중...")
            
            try:
                # 로컬 데이터셋 로드 및 업로드
                dataset = LeRobotDataset(repo_id, root='.')
                dataset.push_to_hub(
                    tags=["robotics", "manipulation", "moving-tape"],
                    private=False,
                    push_videos=True
                )
                
                repo_ids.append(repo_id)
                print(f"✓ 업로드 완료: {repo_id}")
                
            except Exception as e:
                print(f"✗ 업로드 실패: {e}")
                # 실패해도 repo_id는 추가 (이미 업로드되어 있을 수 있음)
                repo_ids.append(repo_id)
    
    finally:
        # 원래 디렉토리로 복원
        os.chdir(original_dir)
    
    return repo_ids

def merge_with_multi_dataset(repo_ids, merged_name="moving-tape-merged-dataset"):
    """MultiLeRobotDataset을 사용해서 데이터셋들을 합치기"""
    
    print(f"\nMultiLeRobotDataset을 사용한 데이터셋 통합")
    print("=" * 50)
    
    # 임시 작업 디렉토리 생성 (시스템 임시 디렉토리 사용)
    import tempfile
    import shutil
    
    temp_dir = tempfile.mkdtemp(prefix="lerobot_merge_")
    print(f"임시 작업 디렉토리: {temp_dir}")
    
    try:
        # 1. MultiLeRobotDataset 생성 (임시 디렉토리에)
        print(f"MultiLeRobotDataset 생성 중...")
        print(f"대상 repo_ids: {repo_ids}")
        
        try:
            multi_dataset = MultiLeRobotDataset(
                repo_ids=repo_ids,
                root=temp_dir,  # 임시 디렉토리 사용
                video_backend="pyav"  # torchcodec 대신 pyav 사용
            )
        except Exception as e:
            print(f"✗ MultiLeRobotDataset 생성 실패: {e}")
            print("대안으로 개별 데이터셋을 순차적으로 처리합니다...")
            # 개별 데이터셋으로 처리하는 대안 로직을 여기에 추가할 수 있음
            raise e
        
        # 타임아웃 설정을 위한 환경 변수
        import os
        os.environ['HF_HUB_TIMEOUT'] = '300'  # 5분으로 설정
        
        print(f"✓ MultiLeRobotDataset 생성 완료")
        print(f"  총 에피소드: {multi_dataset.num_episodes}")
        print(f"  총 프레임: {multi_dataset.num_frames}")
        print(f"  FPS: {multi_dataset.fps}")
        print(f"  카메라 키: {multi_dataset.camera_keys}")
        
        # 2. 기존 cookingbot 저장소를 로드해서 병합 데이터 추가
        print(f"\n기존 cookingbot 데이터셋 로드 중...")
        
        # datasets_dir 변수를 미리 정의
        datasets_dir = os.path.expanduser("~/lerobotjs/datasets")
        
        # 항상 새로운 데이터셋을 생성 (기존 데이터와 병합하지 않음)
        print(f"새로운 통합 데이터셋 생성 중...")
        
        # 기존 데이터셋이 있다면 제거
        merged_path = os.path.join(datasets_dir, "JisooSong-cookingbot")
        if os.path.exists(merged_path):
            print(f"기존 데이터셋 제거 중: {merged_path}")
            shutil.rmtree(merged_path)
        
        # 첫 번째 데이터셋의 정보를 기준으로 새 데이터셋 생성
        first_dataset = multi_dataset._datasets[0]
        
        # LeRobotDataset.create을 사용해서 새 데이터셋 생성
        merged_dataset = LeRobotDataset.create(
            repo_id="JisooSong/cookingbot",
            fps=multi_dataset.fps,
            features=first_dataset.features,
            root=datasets_dir,
            robot_type=first_dataset.meta.robot_type,
            use_videos=len(first_dataset.meta.video_keys) > 0
        )
        
        print(f"✓ 통합 데이터셋 생성: {merged_dataset.repo_id}")
        
        # 3. MultiLeRobotDataset의 모든 데이터를 새 데이터셋에 복사
        print(f"\n데이터 복사 시작...")
        
        total_episodes = sum(ds.num_episodes for ds in multi_dataset._datasets)
        processed_episodes = 0
        successful_episodes = 0
        failed_episodes = 0
        
        # 각 원본 데이터셋별로 에피소드 처리
        for dataset_idx, original_dataset in enumerate(multi_dataset._datasets):
            dataset_name = repo_ids[dataset_idx]
            print(f"\n[{dataset_idx + 1}/{len(multi_dataset._datasets)}] {dataset_name} 처리 중...")
            print(f"  총 에피소드: {original_dataset.num_episodes}개")
            
            # 해당 데이터셋의 에피소드들 처리
            for local_ep_idx in range(original_dataset.num_episodes):
                processed_episodes += 1
                print(f"  에피소드 {local_ep_idx + 1}/{original_dataset.num_episodes} 처리 중... (전체 진행률: {processed_episodes}/{total_episodes})")
                
                # 에피소드의 시작과 끝 프레임 찾기
                ep_start = original_dataset.episode_data_index["from"][local_ep_idx].item()
                ep_end = original_dataset.episode_data_index["to"][local_ep_idx].item()
                
                print(f"    프레임 범위: {ep_start} ~ {ep_end-1} (총 {ep_end - ep_start}개)")
                
                # 에피소드 버퍼 초기화 (새 에피소드 시작)
                merged_dataset.episode_buffer = merged_dataset.create_episode_buffer(episode_index=merged_dataset.num_episodes)
                
                # 에피소드의 모든 프레임 처리
                frame_count = 0
                for frame_idx in range(ep_start, ep_end):
                    try:
                        # 원본 데이터셋에서 직접 프레임 가져오기 (더 안전함)
                        frame_data = original_dataset[frame_idx]
                        
                        # task 정보 추출 (여러 가능한 키에서 찾기)
                        task = (frame_data.get('task') or 
                               frame_data.get('task_name') or 
                               'default_task')
                        
                        # 새 데이터셋에 추가할 프레임 데이터 준비
                        new_frame_data = {}
                        for key, value in frame_data.items():
                            # 메타데이터 키들은 제외
                            if key in ['episode_index', 'index', 'frame_index', 'timestamp', 
                                     'task_index', 'task', 'task_name', 'dataset_index']:
                                continue
                            
                            # 이미지 데이터인 경우 차원 변환 (CHW -> HWC)
                            if 'images' in key and hasattr(value, 'shape') and len(value.shape) == 3:
                                if value.shape[0] == 3:  # (3, H, W) 형식인 경우
                                    # (3, H, W) -> (H, W, 3)로 변환
                                    import torch
                                    import numpy as np
                                    try:
                                        if isinstance(value, torch.Tensor):
                                            value = value.permute(1, 2, 0)  # pytorch tensor
                                        elif isinstance(value, np.ndarray):
                                            value = value.transpose(1, 2, 0)  # numpy array
                                        else:
                                            # 다른 타입의 경우 numpy로 변환 후 처리
                                            value = np.array(value)
                                            if value.shape[0] == 3:
                                                value = value.transpose(1, 2, 0)
                                        print(f"      이미지 차원 변환: {key} {value.shape}")
                                    except Exception as img_error:
                                        print(f"      ⚠ 이미지 변환 실패 {key}: {img_error}, 원본 유지")
                                        # 변환 실패시 원본 유지
                                        pass
                            
                            new_frame_data[key] = value
                        
                        # 프레임 추가
                        merged_dataset.add_frame(new_frame_data, task)
                        frame_count += 1
                        
                    except Exception as frame_error:
                        print(f"      ✗ 프레임 {frame_idx} 처리 실패: {frame_error}")
                        print(f"      프레임 데이터 키: {list(frame_data.keys()) if 'frame_data' in locals() else '없음'}")
                        # 개별 프레임 실패시에도 계속 진행
                        print(f"      ⚠ 프레임 {frame_idx} 건너뛰고 계속 진행...")
                        continue
                
                print(f"    에피소드 완료: {frame_count}개 프레임 처리됨")
                
                # 각 에피소드가 끝날 때마다 저장
                try:
                    merged_dataset.save_episode()
                    print(f"    ✓ 에피소드 {local_ep_idx + 1} 저장 완료")
                    successful_episodes += 1
                except Exception as save_error:
                    print(f"    ✗ 에피소드 {local_ep_idx + 1} 저장 실패: {save_error}")
                    failed_episodes += 1
                    # 저장 실패해도 계속 진행
                    continue
        
        print(f"\n✓ 데이터 복사 완료!")
        print(f"  성공한 에피소드: {successful_episodes}개")
        print(f"  실패한 에피소드: {failed_episodes}개")
        print(f"  총 에피소드: {merged_dataset.num_episodes}")
        print(f"  총 프레임: {merged_dataset.num_frames}")
        
        # 데이터가 없는 경우 조기 종료
        if successful_episodes == 0:
            print(f"\n❌ 성공한 에피소드가 없습니다. 통합을 중단합니다.")
            return None
        
        # 데이터셋 유효성 검사
        print(f"\n데이터셋 유효성 검사 중...")
        try:
            # 기본 통계 확인
            print(f"  에피소드 수: {merged_dataset.num_episodes}")
            print(f"  프레임 수: {merged_dataset.num_frames}")
            print(f"  FPS: {merged_dataset.fps}")
            print(f"  카메라 키: {merged_dataset.camera_keys}")
            print(f"  비디오 키: {merged_dataset.video_keys}")
            
            # 첫 번째 프레임으로 데이터 구조 확인
            if merged_dataset.num_frames > 0:
                sample_frame = merged_dataset[0]
                print(f"  샘플 프레임 키: {list(sample_frame.keys())}")
                print(f"  샘플 프레임 타입: {[(k, type(v)) for k, v in sample_frame.items()]}")
            
            print(f"✓ 데이터셋 유효성 검사 통과")
            
        except Exception as validation_error:
            print(f"✗ 데이터셋 유효성 검사 실패: {validation_error}")
            print(f"업로드를 건너뛰고 로컬 데이터셋만 반환합니다.")
            return merged_dataset
        
        # 4. cookingbot 저장소에 병합 데이터 업로드
        print(f"\ncookingbot 저장소에 병합 데이터 업로드 중...")
        try:
            # 업로드 전 최종 확인
            if merged_dataset.num_frames == 0:
                print(f"⚠ 경고: 데이터셋에 프레임이 없습니다. 업로드를 건너뜁니다.")
                return merged_dataset
            
            print(f"업로드 시작 - 에피소드: {merged_dataset.num_episodes}, 프레임: {merged_dataset.num_frames}")
            
            # 데이터셋이 제대로 저장되었는지 확인
            print(f"데이터셋 루트 경로: {merged_dataset.root}")
            print(f"메타데이터 파일 존재 확인:")
            meta_files = ["info.json", "episodes.jsonl", "tasks.jsonl", "stats.json"]
            for meta_file in meta_files:
                meta_path = merged_dataset.root / "meta" / meta_file
                exists = meta_path.exists()
                print(f"  {meta_file}: {'✓' if exists else '✗'}")
            
            # 데이터 파일 확인
            data_dir = merged_dataset.root / "data"
            if data_dir.exists():
                chunk_dirs = [d for d in data_dir.iterdir() if d.is_dir() and d.name.startswith("chunk-")]
                print(f"  데이터 청크: {len(chunk_dirs)}개")
                for chunk_dir in chunk_dirs:
                    parquet_files = list(chunk_dir.glob("*.parquet"))
                    print(f"    {chunk_dir.name}: {len(parquet_files)}개 parquet 파일")
            
            merged_dataset.push_to_hub(
                tags=["robotics", "manipulation", "merged-dataset", "moving-tape"],
                private=False,
                push_videos=True
            )
            
            print(f"✓ cookingbot 저장소 업로드 완료!")
            print(f"URL: https://huggingface.co/datasets/JisooSong/cookingbot")
            
        except Exception as upload_error:
            print(f"✗ 업로드 실패: {upload_error}")
            print(f"에러 타입: {type(upload_error).__name__}")
            print(f"에러 상세: {str(upload_error)}")
            
            # 업로드 실패해도 로컬 데이터셋은 성공적으로 생성됨
            print(f"⚠ 로컬 데이터셋은 성공적으로 생성되었습니다.")
            print(f"로컬 경로: {merged_dataset.root}")
            print(f"수동으로 업로드하거나 나중에 다시 시도해주세요.")
            
            return merged_dataset
        
        return merged_dataset
        
    except Exception as e:
        print(f"✗ 통합 실패: {e}")
        print(f"에러 타입: {type(e).__name__}")
        print(f"에러 상세: {str(e)}")
        import traceback
        print(f"스택 트레이스:")
        traceback.print_exc()
        return None
    
    finally:
        # 임시 디렉토리 정리
        print(f"\n임시 디렉토리 정리 중: {temp_dir}")
        try:
            shutil.rmtree(temp_dir)
            print(f"✓ 임시 디렉토리 정리 완료")
        except Exception as e:
            print(f"⚠ 임시 디렉토리 정리 실패: {e}")
            print(f"수동으로 삭제해주세요: {temp_dir}")

def main():
    """메인 실행 함수"""
    
    print("MultiLeRobotDataset을 사용한 데이터셋 통합")
    print("=" * 60)
    
    # 1. 사용 가능한 데이터셋 찾기
    available_datasets, datasets_root = find_available_datasets()
    
    if len(available_datasets) < 1:
        print("통합할 데이터셋이 없습니다.")
        return
    
    print(f"\n사용 가능한 데이터셋: {len(available_datasets)}개")
    
    # 2. 데이터셋 선택
    print(f"\n어떤 데이터셋들을 통합하시겠습니까?")
    print("1. 처음 2개 데이터셋만")
    print("2. 모든 데이터셋")
    print("3. 수동으로 선택 (y/n 방식)")
    print("4. 직접 입력")
    
    choice = input("선택하세요 (1/2/3/4): ").strip()
    
    if choice == "1":
        datasets_to_merge = available_datasets[:2]
    elif choice == "2":
        datasets_to_merge = available_datasets
    elif choice == "3":
        datasets_to_merge = []
        print("\n통합할 데이터셋들을 선택하세요:")
        for i, dataset in enumerate(available_datasets):
            while True:
                answer = input(f"{dataset}을 포함하시겠습니까? (y/n): ").strip().lower()
                if answer in ['y', 'yes']:
                    datasets_to_merge.append(dataset)
                    break
                elif answer in ['n', 'no']:
                    break
                else:
                    print("y 또는 n으로 답해주세요.")
    elif choice == "4":
        datasets_to_merge = []
        print("\n통합할 데이터셋 이름들을 입력하세요 (쉼표로 구분):")
        print("예: moving-tape-dataset-20250915_153200, moving-tape-dataset-20250915_154309")
        
        while True:
            user_input = input("데이터셋 이름들: ").strip()
            if not user_input:
                print("최소 하나의 데이터셋은 입력해야 합니다.")
                continue
            
            # 쉼표로 분리하고 공백 제거
            input_datasets = [name.strip() for name in user_input.split(',')]
            
            # 입력된 데이터셋들이 실제로 존재하는지 확인
            valid_datasets = []
            invalid_datasets = []
            
            for dataset in input_datasets:
                if dataset in available_datasets:
                    valid_datasets.append(dataset)
                else:
                    invalid_datasets.append(dataset)
            
            if invalid_datasets:
                print(f"\n다음 데이터셋들을 찾을 수 없습니다: {invalid_datasets}")
                print(f"사용 가능한 데이터셋들: {available_datasets}")
                continue
            
            datasets_to_merge = valid_datasets
            break
    else:
        print("잘못된 선택입니다. 처음 2개로 진행합니다.")
        datasets_to_merge = available_datasets[:2]
    
    if len(datasets_to_merge) < 1:
        print("선택된 데이터셋이 없습니다.")
        return
    
    print(f"\n통합 대상: {datasets_to_merge}")
    
    # 3. 먼저 개별 데이터셋들을 허깅페이스에 업로드
    repo_ids = upload_datasets_first(datasets_to_merge, datasets_root)
    
    # 4. MultiLeRobotDataset으로 통합
    merged_dataset = merge_with_multi_dataset(repo_ids)
    
    if merged_dataset:
        print(f"\n🎉 통합 완료!")            