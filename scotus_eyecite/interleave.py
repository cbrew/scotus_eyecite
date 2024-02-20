
def _paragraphs(text):
    start = 0
    lines = text.splitlines(keepends=True)
    state = "starting"
    chunk = []
    for line in lines:
        match state:
            case "starting":
                state = "whitespace" if line.isspace() else "text"
                chunk.append(line)
            case "whitespace":
                if line.isspace():
                    chunk.append(line)
                else:
                    para = "".join(chunk)
                    end = start + len(para)
                    yield para, start, end
                    start = end
                    chunk =  [line]
                    state = "text"
            case "text":
                if line.isspace():
                    para = "".join(chunk)
                    end = start + len(para)
                    yield para, start, end
                    start = end
                    chunk = [line]
                    state = "whitespace"
                else:
                    chunk.append(line)
    if chunk:
        para = "".join(chunk)
        end = start + len(para)
        yield para, start, end

def paragraphs(text):
        return list(_paragraphs(text))


def interleave(text,spans):
    paras = []
    for text, start, end in paragraphs(text):
        inside =  [span for span in spans
          if (span[0] >= start) and (span[1] <= end)]
        paras.append(dict(text=text,
                          start=start,
                          end=end,
                          spans=inside))

    return paras
