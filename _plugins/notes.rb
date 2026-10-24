# Notes as a small wiki, with no extra gems.
#
# - [[slug]], [[Some Title]], and [[slug|link text]] link to a note or post.
#   A target that is missing or private renders as plain text (class "wanted"),
#   so a public page never links to something that is not on the site.
# - Each note gets `backlinks`: the notes and posts that link to it.
# - A heading like `## 2026-10-24` or `## 2026-10-24 · Diapsalmata` is a study
#   session. Each note gets `sessions`, and `updated` becomes the later of its
#   front matter and its newest session, so a session needs no date bump.
# - site.data.study_log, study_weeks, and study_stats feed /log/.
#
# Only documents Jekyll actually read are seen: in production that means
# published notes, so private notes never resolve, count, or appear.

require "date"

module NotesGraph
  WIKILINK = /\[\[([^\]|\n]+)(?:\|([^\]\n]+))?\]\]/
  # Fenced blocks and inline code are passed through untouched.
  CODE_OR_LINK = /(^(```|~~~).*?^\2[^\n]*$|`[^`\n]+`)|#{WIKILINK}/m
  SESSION = /^##[ \t]+(\d{4}-\d{2}-\d{2})\b[ \t]*(?:[·:—–-][ \t]*)?(.*)$/

  module_function

  def key(text)
    Jekyll::Utils.slugify(text.to_s.strip)
  end

  def to_date(value)
    case value
    when Date then value
    when Time then value.to_date
    when nil, "" then nil
    else Date.parse(value.to_s)
    end
  rescue ArgumentError
    nil
  end

  # Link text with any [[...]] reduced to its label, for headings shown in lists.
  def plain(text)
    text.to_s.gsub(WIKILINK) { (Regexp.last_match(2) || Regexp.last_match(1)).strip }
  end

  def targets(site)
    @targets ||= {}
    @targets[site.object_id] ||= begin
      map = {}
      docs = site.collections["notes"].docs + site.posts.docs
      docs.each { |d| map[d.data["slug"]] ||= d }
      docs.each { |d| map[key(d.data["title"])] ||= d }
      map
    end
  end

  def links_in(content)
    found = []
    content.scan(CODE_OR_LINK) { found << Regexp.last_match(3) if Regexp.last_match(3) }
    found
  end
end

Jekyll::Hooks.register :site, :post_read do |site|
  NotesGraph.instance_variable_set(:@targets, nil)
  notes = site.collections["notes"].docs
  targets = NotesGraph.targets(site)
  log = []

  notes.each do |note|
    sessions = note.content.scan(NotesGraph::SESSION).filter_map do |date, label|
      d = NotesGraph.to_date(date)
      d && { "date" => d, "label" => NotesGraph.plain(label).strip }
    end
    note.data["sessions"] = sessions.sort_by { |s| s["date"] }
    newest = sessions.map { |s| s["date"] }.max
    note.data["updated"] = [NotesGraph.to_date(note.data["updated"]), newest].compact.max
    %w[started finished].each { |k| note.data[k] = NotesGraph.to_date(note.data[k]) if note.data[k] }
    sessions.each { |s| log << s.merge("kind" => "session", "doc" => note) }
  end

  site.posts.docs.each do |post|
    log << { "date" => post.date.to_date, "kind" => "post", "label" => "", "doc" => post }
  end

  backlinks = Hash.new { |h, k| h[k] = [] }
  (notes + site.posts.docs).each do |source|
    NotesGraph.links_in(source.content).each do |target|
      doc = targets[target.strip] || targets[NotesGraph.key(target)]
      backlinks[doc.url] << source if doc && doc != source
    end
  end
  notes.each { |n| n.data["backlinks"] = backlinks[n.url].uniq.sort_by { |d| d.data["title"].to_s } }

  log.sort_by! { |e| [e["date"], e["doc"].data["title"].to_s] }.reverse!
  site.data["study_log"] = log

  # The last 26 weeks, Monday first, oldest on the left.
  today = site.time.to_date
  monday = today - ((today.wday - 1) % 7)
  counts = Hash.new(0)
  log.each { |e| counts[e["date"] - ((e["date"].wday - 1) % 7)] += 1 if e["kind"] == "session" }
  site.data["study_weeks"] = (0...26).map do |i|
    start = monday - (7 * (25 - i))
    { "start" => start, "count" => counts[start] }
  end

  year = today.year
  site.data["study_stats"] = {
    "year" => year,
    "sessions" => log.count { |e| e["kind"] == "session" && e["date"].year == year },
    "books" => notes.count { |n| n.data["finished"]&.year == year },
    "posts" => site.posts.docs.count { |p| p.date.year == year },
    "notes" => notes.size,
  }
end

Jekyll::Hooks.register [:documents], :pre_render do |doc, _payload|
  next unless doc.collection && %w[notes posts].include?(doc.collection.label)

  site = doc.site
  targets = NotesGraph.targets(site)
  doc.content = doc.content.gsub(NotesGraph::CODE_OR_LINK) do
    m = Regexp.last_match
    next m[1] if m[1]

    target = m[3].strip
    hit = targets[target] || targets[NotesGraph.key(target)]
    # A bare slug reads badly as link text; show the title instead.
    text = (m[4] || (hit && target == hit.data["slug"] ? hit.data["title"] : target)).strip
    if hit
      "[#{text}](#{site.baseurl}#{hit.url})"
    else
      text = text.tr("-", " ") if m[4].nil? && text.match?(/\A[a-z0-9-]+\z/)
      %(<span class="wanted" title="Not written yet">#{text}</span>)
    end
  end
end
