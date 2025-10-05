#!/usr/bin/env python
import os
import json

def check_compatibility():
    """두 데이터셋의 호환성 확인"""
    
    folder1 = "moving-tape-dataset-20250915_153200"
    folder2 = "moving-tape-dataset-20250915_154309"
    
    print("데이터셋 호환성 확인")
    print("=" * 40)
    
    # 폴더 존재 확인
    print(f"폴더1 ({folder1}): {'존재' if os.path.exists(folder1) else '없음'}")
    print(f"폴더2 ({folder2}): {'존재' if os.path.exists(folder2) else '없음'}")
    
    if not os.path.exists(folder1) or not os.path.exists(folder2):
        print("필요한 폴더가 없습니다.")
        return False
    
    # info.json 파일 읽기
    info1_path = os.path.join(folder1, 'meta', 'info.json')
    info2_path = os.path.join(folder2, 'meta', 'info.json')
    
    try:
        with open(info1_path, 'r') as f:
            info1 = json.load(f)
        with open(info2_path, 'r') as f:
            info2 = json.load(f)
        
        print(f"\n데이터셋 정보:")
        print("-" * 20)
        
        # 데이터셋1 정보
        print(f"데이터셋1 ({folder1}):")
        print(f"  FPS: {info1.get('fps')}")
        print(f"  로봇: {info1.get('robot_type')}")
        print(f"  에피소드: {info1.get('total_episodes')}")
        print(f"  프레임: {info1.get('total_frames')}")
        print(f"  비디오: {info1.get('video', False)}")
        
        # 데이터셋2 정보  
        print(f"\n데이터셋2 ({folder2}):")
        print(f"  FPS: {info2.get('fps')}")
        print(f"  로봇: {info2.get('robot_type')}")
        print(f"  에피소드: {info2.get('total_episodes')}")
        print(f"  프레임: {info2.get('total_frames')}")
        print(f"  비디오: {info2.get('video', False)}")
        
        # 호환성 비교
        print(f"\n호환성 비교:")
        print("-" * 20)
        
        fps1, fps2 = info1.get('fps'), info2.get('fps')
        fps_ok = fps1 == fps2
        print(f"FPS: {fps1} vs {fps2} -> {'✓' if fps_ok else '✗'}")
        
        robot1, robot2 = info1.get('robot_type'), info2.get('robot_type')  
        robot_ok = robot1 == robot2
        print(f"로봇: {robot1} vs {robot2} -> {'✓' if robot_ok else '✗'}")
        
        video1, video2 = info1.get('video', False), info2.get('video', False)
        video_ok = video1 == video2
        print(f"비디오: {video1} vs {video2} -> {'✓' if video_ok else '✗'}")
        
        # Features 비교
        features1 = set(info1.get('features', {}).keys())
        features2 = set(info2.get('features', {}).keys()) 
        common = features1.intersection(features2)
        
        print(f"Features:")
        print(f"  데이터셋1: {len(features1)}개")
        print(f"  데이터셋2: {len(features2)}개")
        print(f"  공통: {len(common)}개")
        
        if len(common) > 0:
            print(f"  공통 features: {sorted(list(common))}")
        
        diff1 = features1 - features2
        diff2 = features2 - features1  
        if diff1:
            print(f"  데이터셋1 전용: {sorted(list(diff1))}")
        if diff2:
            print(f"  데이터셋2 전용: {sorted(list(diff2))}")
        
        # 결론
        print(f"\n결론:")
        print("=" * 20)
        
        compatible = fps_ok and video_ok and len(common) >= 5
        
        if compatible:
            print("✓ 호환 가능! 두 데이터셋을 합칠 수 있습니다.")
            if not robot_ok:
                print("⚠ 로봇 타입이 다르지만 합치는 것은 가능합니다.")
        else:
            print("✗ 호환에 문제가 있습니다.")
            issues = []
            if not fps_ok:
                issues.append("FPS 불일치")
            if not video_ok:
                issues.append("비디오 형식 불일치")
            if len(common) < 5:
                issues.append("공통 features 부족")
            print(f"문제점: {', '.join(issues)}")
        
        return compatible
        
    except Exception as e:
        print(f"오류 발생: {e}")
        return False

if __name__ == "__main__":
    result = check_compatibility()
    
    if result:
        print("\n다음 단계: 데이터셋 합치기를 진행할 수 있습니다.")
    else:
        print("\n데이터셋을 수정하거나 개별적으로 처리해야 할 수 있습니다.")