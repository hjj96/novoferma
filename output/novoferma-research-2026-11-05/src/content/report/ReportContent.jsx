import React from "react";
import { DataTable, ReportSection, RichNarrative, useDataApp } from "../../data-app-public.jsx";
import content from "./content.json";
import defaultPreviews from "./source-previews.json";

function tableQueryId(section) {
  return section.table?.queryId || `table_${section.id.replace(/[^a-zA-Z0-9_-]/g, "_")}`;
}

function LinkedCell({ value }) {
  if (typeof value !== "string") return value ?? "—";
  const parts = value.split(/(\[[^\]]+\]\(https:\/\/[^)]+\))/g);
  return <>{parts.map((part, i) => {
    const link = part.match(/^\[([^\]]+)\]\((https:\/\/[^)]+)\)$/);
    return link ? <a key={i} href={link[2]} target="_blank" rel="noreferrer">{link[1]}</a> : <React.Fragment key={i}>{part}</React.Fragment>;
  })}</>;
}

export function ReportContent() {
  const { snapshot, reviewedRows, visible, canEdit, mode, appTitle, setAppTitle } = useDataApp();
  const previews = { ...defaultPreviews, ...(content.sourcePreviews || {}) };
  return <article className="report-content nf-research" aria-label="Исследование продуктов НОВОФЕРМА">
    <header className="report-hero">
      <h1 data-data-app-title contentEditable={canEdit && mode === "edit"} suppressContentEditableWarning
        aria-label={canEdit && mode === "edit" ? "Редактировать название отчёта" : undefined}
        onBlur={canEdit && mode === "edit" ? (event) => setAppTitle(event.currentTarget.textContent?.trim() || appTitle) : undefined}
        onKeyDown={canEdit && mode === "edit" ? (event) => { if (event.key === "Enter") { event.preventDefault(); event.currentTarget.blur(); } } : undefined}>{appTitle}</h1>
      {content.introduction && <RichNarrative id="report:introduction" value={content.introduction} sourcePreviews={previews} label="Редактировать введение" />}
    </header>
    <nav className="nf-section-nav" aria-label="Оглавление отчёта">{(content.sections || []).map((section) => <a key={section.id} href={`#nf-${section.id}`}>{section.title}</a>)}</nav>
    {(content.sections || []).map((section) => {
      if (!visible(section.id)) return null;
      const primaryQueryId = section.table ? tableQueryId(section) : (section.queryId || "research_basis");
      const primaryRows = reviewedRows(primaryQueryId);
      const researchQueryId = `research_${section.id.replace(/[^a-zA-Z0-9_-]/g, "_")}`;
      const researchRows = reviewedRows(researchQueryId);
      const queryIds = section.table ? [primaryQueryId, researchQueryId] : [researchQueryId];
      const sourceRowsByQuery = section.table
        ? { [primaryQueryId]: primaryRows, [researchQueryId]: researchRows } : { [researchQueryId]: researchRows };
      const markdown = `${section.title ? `## ${section.title}\n\n` : ""}${section.markdown || ""}`;
      const columns = (section.table?.columns || []).map((column) => ({ ...column, field: column.field || column.key,
        renderCell: (value) => <LinkedCell value={value} /> }));
      return <section key={section.id} id={`nf-${section.id}`} className="nf-section-anchor"><ReportSection id={section.id} title={section.title || "Исследование"}
        queryId={section.table ? primaryQueryId : researchQueryId} queryIds={queryIds} sourceRowsByQuery={sourceRowsByQuery}
        showHeading={false} className="report-section nf-report-section">
        {markdown && <RichNarrative id={`${section.id}:body`} value={markdown} sourcePreviews={previews} label="Редактировать текст раздела" />}
        {section.table && <div className="nf-table" data-reviewed-rows>
          <DataTable rows={primaryRows} columns={columns} searchable={section.table.searchable === true}
            caption={section.table.title || section.title || "Сравнение"} compactNumbers={false} />
        </div>}
        {section.after && <RichNarrative id={`${section.id}:after`} value={section.after} sourcePreviews={previews} label="Редактировать вывод" />}
      </ReportSection></section>;
    })}
  </article>;
}
