import difflib

def is_similar_text(t1: str, t2: str, char_threshold: float = 0.8, word_threshold: float = 0.66):
    """
    So sánh độ tương đồng giữa 2 chuỗi text để tính evaluation metrics.
    - char_threshold: Ngưỡng tương đồng theo ký tự (VD: 0.8 = giống nhau 80% số ký tự)
    - word_threshold: Ngưỡng tương đồng theo số lượng từ (word-level)
    """
    t1_c = str(t1).strip().lower()
    t2_c = str(t2).strip().lower()
    
    if not t1_c or not t2_c:
        return False
        
    # 1. Khớp hoàn toàn (Fast path)
    if t1_c == t2_c:
        return True
        
    # 2. Khớp theo độ tương đồng ký tự (Levenshtein distance)
    # Ví dụ: "TP.HCM" và "TP. HCM" hoặc "Hà Nôi" và "Hà Nội"
    char_sim = difflib.SequenceMatcher(None, t1_c, t2_c).ratio()
    if char_sim >= char_threshold:
        return True
        
    # 3. Khớp theo độ phủ từ (Token/Word Overlap)
    # Rất hữu ích cho entity tiếng Việt dài. 
    # Ví dụ: "Cổng thông tin điện tử Bộ Tài chính" vs "Cổng thông tin điện tử Bộ Tài chính và Kho bạc Nhà nước"
    tokens1 = set(t1_c.split())
    tokens2 = set(t2_c.split())
    
    if tokens1 and tokens2:
        intersection = tokens1.intersection(tokens2)
        
        # Tỷ lệ từ trùng lặp so với chuỗi ngắn hơn (Recall của cụm từ)
        min_len = min(len(tokens1), len(tokens2))
        max_len = max(len(tokens1), len(tokens2))
        
        overlap_ratio = len(intersection) / min_len
        global_ratio = len(intersection) / max_len
        
        # Điều kiện: Chuỗi ngắn phải nằm gần như trọn vẹn trong chuỗi dài (>= word_threshold)
        # VÀ để tránh việc 1 từ chung chung (như "ông") khớp với cả cụm dài ("ông Nguyễn Văn A"), 
        # tỷ lệ phủ trên toàn bộ chuỗi dài cũng không được quá thấp (vd: >= 0.4).
        if overlap_ratio >= word_threshold and global_ratio >= 0.4:
            return True

    return False