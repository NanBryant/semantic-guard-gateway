from core.sentence_splitter import split_sentences


def texts(items):
    return [item["text"] for item in items]


def test_split_chinese_prompt_and_sentences():
    result = split_sentences("请帮我润色：这个方案已经通过评审。下季度准备试点。")
    assert texts(result) == ["请帮我润色：", "这个方案已经通过评审。", "下季度准备试点。"]
    assert [item["sentence_id"] for item in result] == ["s1", "s2", "s3"]


def test_split_single_sentence_without_punctuation():
    result = split_sentences("这个方案基本定了，只差最后签字")
    assert texts(result) == ["这个方案基本定了，只差最后签字"]


def test_split_newlines_and_demo_ordinal_text():
    result = split_sentences("第一句第二句。第三句？\n第四句")
    assert texts(result) == ["第一句", "第二句。", "第三句？", "第四句"]
