from yattag import Doc

def paras(text):
    chunk = []
    start = 0
    state = "starting"
    for line in text.splitlines(keepends=True):
        match state:
            case "starting":
                chunk.append(line)
                state = "whitespace" if line.isspace() else "nonwhitespace"
            case "whitespace":
                if line.isspace():
                    chunk.append(line)
                else:
                    tx = "".join(chunk)
                    end = start + len(tx)
                    yield dict(text=tx,start=start,end=end,type="whitespace")
                    start = end
                    state = "nonwhitespace"
                    chunk = [line]
            case "nonwhitespace":
                if not line.isspace():
                    chunk.append(line)
                else:
                    tx = "".join(chunk)
                    end = start + len(tx)
                    yield dict(text=tx, start=start, end=end, type="nonwhitespace")
                    start = end
                    state = "whitespace"
                    chunk = [line]
    if chunk:
        tx = "".join(chunk)
        yield dict(text=tx, start=start, end=len(text), type="whitespace" if tx.isspace() else "nonwhitespace")


def present(fulltext,spans):
    doc, tag, text = Doc().tagtext()
    interleaved = list(interleave(fulltext,spans))
    state = "nonspace"
    with tag('html'):
        with tag('body'):
            while True:
                tx,tt = interleaved[0]
                match state:
                    case "space":
                        if tt == "space":
                            interleaved = interleaved[1:]
                            if not interleaved:
                                return doc.getvalue()
                        else:
                            state = "nonspace"
                    case "nonspace":
                        with tag("p"):
                            while tt != "space":
                                with tag("span", style="border: black 2px solid" if tt == "cite" else "color:blue"):
                                    text(tx)
                                    interleaved = interleaved[1:]
                                    if interleaved:
                                        tx,tt = interleaved[0]
                                    else:
                                        return doc.getvalue()
                        # now at first space after non-spaces
                        doc.stag("hr")
                        interleaved = interleaved[1:]
                        if not interleaved:
                            return doc.getvalue()
                        state = "space"


def interleave(text,spans):
    paras = []
    start = 0
    for span in spans:
        if span['start'] == start:
            paras.append((span['text'], "cite"))
            start = span['end']
        elif span['start'] > start:
            for para in paras2(text[start:span['start']]):
                paras.append(para)
            paras.append((span['text'],"cite"))
            start = span['end']
    if start < len(text):
        for para in paras2(text[start:]):
            paras.append(para)
    return paras

def paras2(text):
    lines = text.splitlines(keepends=True)
    if len(lines) == 0:
        return
    chunk = [lines[0]]
    for line in lines[1:]:
        if chunk[-1].isspace() and line.isspace():
            chunk.append(line)
        elif not chunk[-1].isspace() and not line.isspace():
            chunk.append(line)
        elif chunk[-1].isspace() and not line.isspace():
            yield "".join(chunk),"space"
            chunk = [line]
        elif not chunk[-1].isspace() and line.isspace():
            yield "".join(chunk),"nonspace"
            chunk = [line]
    if chunk:
        yield "".join(chunk),"space" if chunk[-1].isspace() else "nonspace"
