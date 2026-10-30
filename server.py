import os
from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from database import (
    init_db, aggiungi_evento, modifica_evento, ottieni_eventi, elimina_evento, toggle_completato,
    aggiungi_documento_spesa, modifica_documento_spesa, ottieni_documenti_spesa, elimina_documento_spesa,
    aggiungi_misura, modifica_misura, ottieni_misure, elimina_misura,
    aggiungi_intrattenimento, modifica_intrattenimento, ottieni_intrattenimento, elimina_intrattenimento,
    aggiungi_pomodoro_task, ottieni_pomodoro_tasks, toggle_pomodoro_task, elimina_pomodoro_task, elimina_completati_pomodoro,
    aggiungi_capo, ottieni_armadio, elimina_capo,
    aggiungi_record, ottieni_record, elimina_record,
    aggiungi_scheda_allenamento, modifica_scheda_allenamento, ottieni_schede_allenamento, elimina_scheda_allenamento,
    aggiungi_ricetta, modifica_ricetta, ottieni_ricette, elimina_ricetta
)
from datetime import datetime, timedelta

app = FastAPI()

init_db()

@app.get("/", response_class=HTMLResponse)
def home():
    eventi = ottieni_eventi()
    spesa_docs = ottieni_documenti_spesa()
    misure_items = ottieni_misure()
    media_items = ottieni_intrattenimento()
    pomodoro_items = ottieni_pomodoro_tasks()
    armadio_items = ottieni_armadio()
    record_items = ottieni_record()
    schede_items = ottieni_schede_allenamento()
    ricette_items = ottieni_ricette()
    
    totale_eventi = len(eventi)
    completati_eventi = sum(1 for e in eventi if e[5] == 1)
    
    # --- Agenda HTML ---
    lista_eventi_html = ""
    if not eventi:
        lista_eventi_html = "<div style='text-align: center; padding: 25px; color: #64748b; font-size: 12px; letter-spacing: 2px;'>// NESSUN DATO IN MEMORIA //</div>"
    else:
        for ev in eventi:
            data_formattata = ev[2].rsplit(':', 1)[0] if len(ev[2]) > 16 else ev[2]
            prio = ev[4]
            prio_color = "#f43f5e" if prio == "Urgente" else ("#38bdf8" if prio == "Bassa" else "#fbbf24")
            prio_bg = "rgba(244, 63, 94, 0.15)" if prio == "Urgente" else ("rgba(56, 189, 248, 0.15)" if prio == "Bassa" else "rgba(251, 191, 36, 0.15)")
            
            is_completed = ev[5] == 1
            card_opacity = "0.4" if is_completed else "1"
            title_decoration = "line-through" if is_completed else "none"
            check_bg = "var(--accent-color)" if is_completed else "transparent"
            check_text = "✓" if is_completed else ""
            dt_val_input = ev[2].replace(" ", "T")[:16]

            lista_eventi_html += f"""
            <div class="evento-card cyber-card" data-titolo="{ev[1].lower()}" data-stato="{'completato' if is_completed else 'incompleto'}" data-prio="{prio.lower()}" style="opacity: {card_opacity}; border-left: 4px solid {prio_color}; margin-bottom: 12px;">
                <div id="view_ev_{ev[0]}">
                    <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 6px;">
                        <div style="font-size: 15px; font-weight: 700; color: #f8fafc; text-decoration: {title_decoration}; word-break: break-word; padding-right: 8px;">{ev[1]}</div>
                        <form action="/toggle_evento/{ev[0]}" method="post" style="margin: 0;">
                            <button type="submit" style="width: 24px; height: 24px; border-radius: 6px; border: 2px solid var(--accent-color); background: {check_bg}; color: var(--bg-color); font-weight: bold; cursor: pointer; display: flex; align-items: center; justify-content: center; font-size: 12px;">{check_text}</button>
                        </form>
                    </div>
                    <div style="display: flex; gap: 8px; align-items: center; margin-bottom: 6px;">
                        <span style="background: {prio_bg}; color: {prio_color}; padding: 2px 6px; border-radius: 4px; font-size: 9px; font-weight: 800; text-transform: uppercase;">{prio}</span>
                        <span class="data-evento" data-timestamp="{ev[2]}" style="color: var(--accent-color); font-size: 11px; font-family: monospace;">⚡ {data_formattata}</span>
                    </div>
                    {('<div style="color: #94a3b8; font-size: 12px; margin-top: 4px; background: rgba(15, 23, 42, 0.6); padding: 6px 8px; border-radius: 6px; border: 1px dashed rgba(56,189,248,0.2);">' + ev[3] + '</div>') if ev[3] else ''}
                    <div style="display: flex; gap: 6px; border-top: 1px solid rgba(255,255,255,0.08); padding-top: 10px; margin-top: 10px;">
                        <button type="button" onclick="mostraModifica('ev', {ev[0]})" style="flex: 1; background: rgba(56, 189, 248, 0.1); color: var(--accent-color); border: 1px solid var(--accent-border); padding: 6px; border-radius: 6px; cursor: pointer; font-size: 10px; font-weight: 700; text-transform: uppercase;">✏️ Modifica</button>
                        <a href="/ics/{ev[0]}" style="flex: 1; background: rgba(56, 189, 248, 0.1); color: var(--accent-color); border: 1px solid var(--accent-border); text-align: center; padding: 6px; border-radius: 6px; text-decoration: none; font-size: 10px; font-weight: 700; text-transform: uppercase;">🔔 Sync</a>
                        <form action="/elimina_evento/{ev[0]}" method="post" style="margin: 0; flex: 1;">
                            <button type="submit" style="width: 100%; background: rgba(244, 63, 94, 0.1); color: #f43f5e; border: 1px solid rgba(244, 63, 94, 0.3); padding: 6px; border-radius: 6px; cursor: pointer; font-size: 10px; font-weight: 700; text-transform: uppercase;">🗑️ Elimina</button>
                        </form>
                    </div>
                </div>
                <div id="edit_ev_{ev[0]}" style="display: none;">
                    <form action="/modifica_evento/{ev[0]}#tab-agenda" method="post">
                        <div style="font-size: 12px; font-weight: 900; color: var(--accent-color); margin-bottom: 8px; text-transform: uppercase;">✏️ Modifica Evento</div>
                        <label>Oggetto</label><input type="text" name="titolo" value="{ev[1]}" required>
                        <label>Data e Ora</label><input type="datetime-local" name="data_ora" value="{dt_val_input}" required>
                        <label>Priorità</label>
                        <select name="priorita">
                            <option value="Ordinario" {'selected' if prio=='Ordinario' else ''}>⚡ Ordinario</option>
                            <option value="Urgente" {'selected' if prio=='Urgente' else ''}>🔥 Urgente / Critico</option>
                            <option value="Bassa" {'selected' if prio=='Bassa' else ''}>💤 Bassa Priorità</option>
                        </select>
                        <label>Dettagli</label><input type="text" name="descrizione" value="{ev[3]}">
                        <div style="display: flex; gap: 6px;">
                            <button type="submit" class="btn-salva" style="flex: 1;">Salva</button>
                            <button type="button" onclick="nascondiModifica('ev', {ev[0]})" style="flex: 1; background: rgba(255,255,255,0.1); color: #fff; border: none; border-radius: 8px; font-weight: bold; cursor: pointer; text-transform: uppercase; font-size: 11px;">Annulla</button>
                        </div>
                    </form>
                </div>
            </div>
            """

    # --- Spesa HTML ---
    lista_spesa_html = ""
    if not spesa_docs:
        lista_spesa_html = "<div style='text-align: center; padding: 25px; color: #64748b; font-size: 12px; letter-spacing: 2px;'>// NESSUN DOCUMENTO SPESA //</div>"
    else:
        for doc in spesa_docs:
            doc_id, doc_titolo, raw_data = doc[0], doc[1], doc[2]
            negozi_html = ""
            for riga in raw_data.split("\n"):
                if ":" in riga:
                    negozio_nome, articoli_str = riga.split(":", 1)
                    negozio_nome, articoli = negozio_nome.strip(), [art.strip() for art in articoli_str.split(",") if art.strip()]
                    if not articoli: continue
                    articoli_li = ""
                    for idx, art in enumerate(articoli):
                        art_id = f"doc_{doc_id}_{abs(hash(negozio_nome))}_{idx}"
                        articoli_li += f"""
                        <li style="margin-bottom: 6px; display: flex; align-items: center; justify-content: space-between;">
                            <span id="txt_{art_id}" style="color: #f8fafc; font-size: 13px;">{art}</span>
                            <button type="button" onclick="toggleArticolo('{art_id}')" id="btn_{art_id}" style="width: 20px; height: 20px; border-radius: 4px; border: 2px solid var(--accent-color); background: transparent; color: var(--bg-color); font-weight: bold; cursor: pointer; display: flex; align-items: center; justify-content: center; font-size: 10px;"></button>
                        </li>
                        """
                    negozi_html += f"""
                    <div style="background: rgba(15, 23, 42, 0.5); padding: 10px; border-radius: 8px; margin-bottom: 8px; border: 1px solid rgba(56, 189, 248, 0.15);">
                        <div style="color: var(--accent-color); font-size: 13px; font-weight: 800; margin-bottom: 6px; text-transform: uppercase;">🏪 {negozio_nome}</div>
                        <ul style="list-style: none; padding: 0; margin: 0;">{articoli_li}</ul>
                    </div>
                    """
            lista_spesa_html += f"""
            <div class="cyber-card" style="margin-bottom: 14px; border-left: 4px solid var(--accent-color);">
                <div id="view_spesa_{doc_id}">
                    <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 10px;">
                        <div style="font-size: 15px; font-weight: 700; color: #ffffff;">📋 {doc_titolo}</div>
                        <div style="display: flex; gap: 6px;">
                            <button type="button" onclick="mostraModifica('spesa', {doc_id})" style="background: rgba(56, 189, 248, 0.1); color: var(--accent-color); border: 1px solid var(--accent-border); padding: 4px 8px; border-radius: 6px; cursor: pointer; font-size: 11px;">✏️</button>
                            <form action="/elimina_spesa/{doc_id}" method="post" style="margin: 0;"><button type="submit" style="background: rgba(244, 63, 94, 0.1); color: #f43f5e; border: 1px solid rgba(244, 63, 94, 0.3); padding: 4px 8px; border-radius: 6px; cursor: pointer; font-size: 11px;">🗑️</button></form>
                        </div>
                    </div>
                    {negozi_html}
                </div>
                <div id="edit_spesa_{doc_id}" style="display: none;">
                    <form action="/modifica_spesa/{doc_id}#tab-spesa" method="post">
                        <div style="font-size: 12px; font-weight: 900; color: var(--accent-color); margin-bottom: 8px; text-transform: uppercase;">✏️ Modifica Spesa</div>
                        <label>Titolo</label><input type="text" name="titolo_documento" value="{doc_titolo}" required>
                        <label>Negozi e Articoli</label><textarea name="negozi_articoli" rows="4" required>{raw_data}</textarea>
                        <div style="display: flex; gap: 6px;"><button type="submit" class="btn-salva" style="flex:1;">Salva</button><button type="button" onclick="nascondiModifica('spesa', {doc_id})" style="flex:1; background: rgba(255,255,255,0.1); color:#fff; border:none; border-radius:8px; font-weight:bold; cursor:pointer; font-size:11px;">Annulla</button></div>
                    </form>
                </div>
            </div>
            """

    # --- Misure HTML ---
    lista_misure_html = ""
    if not misure_items:
        lista_misure_html = "<div style='text-align: center; padding: 25px; color: #64748b; font-size: 12px; letter-spacing: 2px;'>// NESSUNA MISURA REGISTRATA //</div>"
    else:
        for m in misure_items:
            dettagli_html = ""
            if m[3]: dettagli_html += f"<div style='margin-bottom: 4px;'>• <b>{m[2]}:</b> {m[3]}</div>"
            if m[5]: dettagli_html += f"<div style='margin-bottom: 4px;'>• <b>{m[4]}:</b> {m[5]}</div>"
            if m[7]: dettagli_html += f"<div style='margin-bottom: 4px;'>• <b>{m[6]}:</b> {m[7]}</div>"
            note_html = ""
            if m[8]:
                note_li = ""
                for idx, art in enumerate([a.strip() for a in m[8].split(",") if a.strip()]):
                    art_id = f"misura_{m[0]}_{idx}"
                    note_li += f"""
                    <li style="margin-bottom: 6px; display: flex; align-items: center; justify-content: space-between;">
                        <span id="txt_{art_id}" style="color: #94a3b8; font-size: 12px;">{art}</span>
                        <button type="button" onclick="toggleArticolo('{art_id}')" id="btn_{art_id}" style="width: 20px; height: 20px; border-radius: 4px; border: 2px solid var(--accent-color); background: transparent; color: var(--bg-color); font-weight: bold; cursor: pointer; display: flex; align-items: center; justify-content: center; font-size: 10px;"></button>
                    </li>
                    """
                note_html = f"<div style='margin-top: 10px; background: rgba(15, 23, 42, 0.5); padding: 10px; border-radius: 8px; border: 1px dashed rgba(56, 189, 248, 0.3);'><div style='color: var(--accent-color); font-size: 11px; font-weight: 800; margin-bottom: 6px; text-transform: uppercase;'>🛠️ Materiale Extra</div><ul style='list-style: none; padding: 0; margin: 0;'>{note_li}</ul></div>"
            
            lista_misure_html += f"""
            <div class="cyber-card" style="margin-bottom: 14px; border-left: 4px solid var(--accent-color);">
                <div id="view_misura_{m[0]}">
                    <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 8px;">
                        <div style="font-size: 15px; font-weight: 700; color: var(--accent-color);">📐 {m[1]}</div>
                        <div style="display: flex; gap: 6px;">
                            <button type="button" onclick="mostraModifica('misura', {m[0]})" style="background: rgba(56, 189, 248, 0.1); color: var(--accent-color); border: 1px solid var(--accent-border); padding: 4px 8px; border-radius: 6px; cursor: pointer; font-size: 11px;">✏️</button>
                            <form action="/elimina_misura/{m[0]}" method="post" style="margin: 0;"><button type="submit" style="background: rgba(244, 63, 94, 0.1); color: #f43f5e; border: 1px solid rgba(244, 63, 94, 0.3); padding: 4px 8px; border-radius: 6px; cursor: pointer; font-size: 11px;">🗑️</button></form>
                        </div>
                    </div>
                    <div style="color: #f8fafc; font-size: 13px; font-family: monospace; background: rgba(15, 23, 42, 0.4); padding: 8px 10px; border-radius: 8px;">{dettagli_html}</div>
                    {note_html}
                </div>
                <div id="edit_misura_{m[0]}" style="display: none;">
                    <form action="/modifica_misura/{m[0]}#tab-misure" method="post">
                        <div style="font-size: 12px; font-weight: 900; color: var(--accent-color); margin-bottom: 8px; text-transform: uppercase;">✏️ Modifica Misure</div>
                        <label>Prodotto</label><input type="text" name="prodotto" value="{m[1]}" required>
                        <div style="display: flex; gap: 6px; margin-bottom: 8px;">
                            <input type="text" name="m1_tipo" value="{m[2]}" style="flex:1; margin-bottom:0;" required>
                            <input type="text" name="m1_val" value="{m[3]}" style="flex:1; margin-bottom:0;" required>
                        </div>
                        <div style="display: flex; gap: 6px; margin-bottom: 8px;">
                            <input type="text" name="m2_tipo" value="{m[4]}" style="flex:1; margin-bottom:0;">
                            <input type="text" name="m2_val" value="{m[5]}" style="flex:1; margin-bottom:0;">
                        </div>
                        <div style="display: flex; gap: 6px; margin-bottom: 8px;">
                            <input type="text" name="m3_tipo" value="{m[6]}" style="flex:1; margin-bottom:0;">
                            <input type="text" name="m3_val" value="{m[7]}" style="flex:1; margin-bottom:0;">
                        </div>
                        <label>Note Extra</label><input type="text" name="note_extra" value="{m[8] if m[8] else ''}">
                        <div style="display: flex; gap: 6px;"><button type="submit" class="btn-salva" style="flex:1;">Salva</button><button type="button" onclick="nascondiModifica('misura', {m[0]})" style="flex:1; background: rgba(255,255,255,0.1); color:#fff; border:none; border-radius:8px; font-weight:bold; cursor:pointer; font-size:11px;">Annulla</button></div>
                    </form>
                </div>
            </div>
            """

    # --- Film & TV HTML ---
    lista_media_html = ""
    if not media_items:
        lista_media_html = "<div style='text-align: center; padding: 25px; color: #64748b; font-size: 12px; letter-spacing: 2px;'>// ARCHIVIO MEDIA VUOTO //</div>"
    else:
        for med in media_items:
            badge_color = "#38bdf8" if med[2] == "Film" else "#a855f7"
            voto_val = med[5]
            stelle_html = "⭐" * int(voto_val) if (voto_val and voto_val.isdigit()) else "Non valutato"
            lista_media_html += f"""
            <div class="cyber-card media-card" data-genere="{med[3]}" data-stato="{med[4]}" data-voto="{voto_val if voto_val else '0'}" style="margin-bottom: 12px; border-left: 4px solid {badge_color};">
                <div id="view_media_{med[0]}">
                    <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 6px;">
                        <div style="font-size: 15px; font-weight: 700; color: #ffffff;">🍿 {med[1]}</div>
                        <div style="display: flex; gap: 6px;">
                            <button type="button" onclick="mostraModifica('media', {med[0]})" style="background: rgba(56, 189, 248, 0.1); color: var(--accent-color); border: 1px solid var(--accent-border); padding: 4px 8px; border-radius: 6px; cursor: pointer; font-size: 11px;">✏️</button>
                            <form action="/elimina_media/{med[0]}" method="post" style="margin: 0;"><button type="submit" style="background: rgba(244, 63, 94, 0.1); color: #f43f5e; border: 1px solid rgba(244, 63, 94, 0.3); padding: 4px 8px; border-radius: 6px; cursor: pointer; font-size: 11px;">🗑️</button></form>
                        </div>
                    </div>
                    <div style="display: flex; gap: 8px; align-items: center; font-size: 11px; flex-wrap: wrap;">
                        <span style="background: {badge_color}25; color: {badge_color}; padding: 2px 6px; border-radius: 4px; font-weight: 800; text-transform: uppercase;">{med[2]}</span>
                        <span style="color: #cbd5e1; background: rgba(15, 23, 42, 0.6); padding: 2px 6px; border-radius: 4px; font-weight: 600;">{med[3]}</span>
                        <span style="color: #94a3b8; background: rgba(15, 23, 42, 0.6); padding: 2px 6px; border-radius: 4px;">📌 {med[4]}</span>
                        <span style="color: #fbbf24; font-weight: 700; margin-left: auto;">{stelle_html}</span>
                    </div>
                </div>
                <div id="edit_media_{med[0]}" style="display: none;">
                    <form action="/modifica_media/{med[0]}#tab-media" method="post">
                        <div style="font-size: 12px; font-weight: 900; color: var(--accent-color); margin-bottom: 8px; text-transform: uppercase;">✏️ Modifica Media</div>
                        <label>Titolo</label><input type="text" name="titolo" value="{med[1]}" required>
                        <div style="display: flex; gap: 10px;">
                            <div style="flex:1;"><label>Genere</label><input type="text" name="genere" value="{med[3]}" required></div>
                            <div style="flex:1;"><label>Tipologia</label>
                                <select name="tipo"><option value="Film" {'selected' if med[2]=='Film' else ''}>🎬 Film</option><option value="Serie TV" {'selected' if med[2]=='Serie TV' else ''}>📺 Serie TV</option></select>
                            </div>
                        </div>
                        <div style="display: flex; gap: 10px;">
                            <div style="flex:1;"><label>Stato</label>
                                <select name="stato"><option value="Da Vedere" {'selected' if med[4]=='Da Vedere' else ''}>⏳ Da Vedere</option><option value="In Corso" {'selected' if med[4]=='In Corso' else ''}>⚡ In Corso</option><option value="Completato" {'selected' if med[4]=='Completato' else ''}>✓ Completato</option></select>
                            </div>
                            <div style="flex:1;"><label>Valutazione</label>
                                <select name="voto">
                                    <option value="">Da valutare</option>
                                    <option value="5" {'selected' if med[5]=='5' else ''}>⭐⭐⭐⭐⭐</option>
                                    <option value="4" {'selected' if med[5]=='4' else ''}>⭐⭐⭐⭐</option>
                                    <option value="3" {'selected' if med[5]=='3' else ''}>⭐⭐⭐</option>
                                    <option value="2" {'selected' if med[5]=='2' else ''}>⭐⭐</option>
                                    <option value="1" {'selected' if med[5]=='1' else ''}>⭐</option>
                                </select>
                            </div>
                        </div>
                        <div style="display: flex; gap: 6px;"><button type="submit" class="btn-salva" style="flex:1;">Salva</button><button type="button" onclick="nascondiModifica('media', {med[0]})" style="flex:1; background: rgba(255,255,255,0.1); color:#fff; border:none; border-radius:8px; font-weight:bold; cursor:pointer; font-size:11px;">Annulla</button></div>
                    </form>
                </div>
            </div>
            """

    # --- Pomodoro Tasks HTML ---
    lista_pomodoro_html = ""
    if not pomodoro_items:
        lista_pomodoro_html = "<div style='text-align: center; padding: 15px; color: #64748b; font-size: 11px;'>// NESSUN OBIETTIVO FOCUS //</div>"
    else:
        for t in pomodoro_items:
            t_id, t_testo, t_cat, t_comp = t[0], t[1], t[2], t[3]
            chk_bg = "var(--accent-color)" if t_comp == 1 else "transparent"
            chk_txt = "✓" if t_comp == 1 else ""
            t_style = "line-through; opacity: 0.4;" if t_comp == 1 else "none; opacity: 1;"
            cat_color = "#38bdf8" if t_cat == "Studio" else ("#a855f7" if t_cat == "Lavoro" else "#22c55e")
            
            lista_pomodoro_html += f"""
            <div style="display: flex; align-items: center; justify-content: space-between; background: rgba(15,23,42,0.6); padding: 8px 10px; border-radius: 8px; margin-bottom: 6px; border: 1px solid var(--accent-border);">
                <div style="display: flex; align-items: center; gap: 8px;">
                    <span style="background: {cat_color}25; color: {cat_color}; font-size: 8px; padding: 2px 5px; border-radius: 4px; font-weight: 800; text-transform: uppercase;">{t_cat}</span>
                    <span style="color: #f8fafc; font-size: 13px; text-decoration: {t_style}">{t_testo}</span>
                </div>
                <div style="display: flex; gap: 6px; align-items: center;">
                    <form action="/toggle_pomodoro/{t_id}" method="post" style="margin:0;"><button type="submit" style="width: 20px; height: 20px; border-radius: 4px; border: 2px solid var(--accent-color); background: {chk_bg}; color: var(--bg-color); font-weight: bold; cursor: pointer; display: flex; align-items: center; justify-content: center; font-size: 10px;">{chk_txt}</button></form>
                    <form action="/elimina_pomodoro/{t_id}" method="post" style="margin:0;"><button type="submit" style="background: transparent; border: none; color: #f43f5e; cursor: pointer; font-size: 11px;">🗑️</button></form>
                </div>
            </div>
            """

    # --- Armadio HTML ---
    lista_armadio_html = ""
    if not armadio_items:
        lista_armadio_html = "<div style='text-align: center; padding: 25px; color: #64748b; font-size: 12px; letter-spacing: 2px;'>// ARMADIO VUOTO //</div>"
    else:
        for item in armadio_items:
            a_id, capo, cat, colore, stagione, pos = item[0], item[1], item[2], item[3], item[4], item[5]
            lista_armadio_html += f"""
            <div class="cyber-card" style="margin-bottom: 12px; border-left: 4px solid #ec4899;">
                <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 6px;">
                    <div style="font-size: 15px; font-weight: 700; color: #ffffff;">🧥 {capo}</div>
                    <form action="/elimina_capo/{a_id}" method="post" style="margin: 0;"><button type="submit" style="background: rgba(244, 63, 94, 0.1); color: #f43f5e; border: 1px solid rgba(244, 63, 94, 0.3); padding: 4px 8px; border-radius: 6px; cursor: pointer; font-size: 11px;">🗑️</button></form>
                </div>
                <div style="display: flex; gap: 6px; align-items: center; font-size: 11px; flex-wrap: wrap;">
                    <span style="background: rgba(236, 72, 153, 0.15); color: #ec4899; padding: 2px 6px; border-radius: 4px; font-weight: 800; text-transform: uppercase;">{cat}</span>
                    <span style="color: #cbd5e1; background: rgba(15, 23, 42, 0.6); padding: 2px 6px; border-radius: 4px;">🎨 {colore}</span>
                    <span style="color: #38bdf8; background: rgba(15, 23, 42, 0.6); padding: 2px 6px; border-radius: 4px;">🌤️ {stagione}</span>
                    <span style="color: #94a3b8; background: rgba(15, 23, 42, 0.6); padding: 2px 6px; border-radius: 4px; margin-left: auto;">📍 {pos}</span>
                </div>
            </div>
            """

    # --- Record Personali HTML ---
    lista_record_html = ""
    if not record_items:
        lista_record_html = "<div style='text-align: center; padding: 15px; color: #64748b; font-size: 11px;'>// NESSUN RECORD REGISTRATO //</div>"
    else:
        for rec in record_items:
            r_id, r_es, r_val, r_data = rec[0], rec[1], rec[2], rec[3]
            lista_record_html += f"""
            <div style="display: flex; align-items: center; justify-content: background; background: rgba(15, 23, 42, 0.6); padding: 8px 10px; border-radius: 8px; margin-bottom: 6px; border: 1px solid rgba(34,197,94,0.3);">
                <div style="flex: 1;"><strong style="color: #22c55e; font-size: 13px;">🏆 {r_es}</strong><div style="color: #cbd5e1; font-size: 12px; font-family: monospace;">{r_val} <span style="color: #64748b; font-size: 10px;">({r_data})</span></div></div>
                <form action="/elimina_record/{r_id}" method="post" style="margin:0;"><button type="submit" style="background: transparent; border: none; color: #f43f5e; cursor: pointer; font-size: 11px;">🗑️</button></form>
            </div>
            """

    # --- Schede Allenamento HTML ---
    lista_schede_html = ""
    if not schede_items:
        lista_schede_html = "<div style='text-align: center; padding: 15px; color: #64748b; font-size: 11px;'>// NESSUNA SCHEDA INSERITA //</div>"
    else:
        for sch in schede_items:
            s_id, s_giorno, s_det = sch[0], sch[1], sch[2]
            lista_schede_html += f"""
            <div class="cyber-card" style="margin-bottom: 12px; border-left: 4px solid #22c55e;">
                <div id="view_scheda_{s_id}">
                    <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 6px;">
                        <div style="font-size: 14px; font-weight: 700; color: #ffffff;">📋 {s_giorno}</div>
                        <div style="display: flex; gap: 6px;">
                            <button type="button" onclick="mostraModifica('scheda', {s_id})" style="background: rgba(34,197,94,0.1); color: #22c55e; border: 1px solid rgba(34,197,94,0.3); padding: 4px 8px; border-radius: 6px; cursor: pointer; font-size: 11px;">✏️</button>
                            <form action="/elimina_scheda/{s_id}" method="post" style="margin: 0;"><button type="submit" style="background: rgba(244, 63, 94, 0.1); color: #f43f5e; border: 1px solid rgba(244, 63, 94, 0.3); padding: 4px 8px; border-radius: 6px; cursor: pointer; font-size: 11px;">🗑️</button></form>
                        </div>
                    </div>
                    <div style="color: #cbd5e1; font-size: 12px; white-space: pre-wrap; background: rgba(5,7,12,0.5); padding: 8px; border-radius: 6px; font-family: monospace;">{s_det}</div>
                </div>
                <div id="edit_scheda_{s_id}" style="display: none;">
                    <form action="/modifica_scheda/{s_id}#tab-allenamento" method="post">
                        <div style="font-size: 12px; font-weight: 900; color: #22c55e; margin-bottom: 8px; text-transform: uppercase;">✏️ Modifica Scheda</div>
                        <label>Giorno / Nome</label><input type="text" name="giorno" value="{s_giorno}" required>
                        <label>Esercizi e Serie</label><textarea name="dettagli_esercizi" rows="4" required>{s_det}</textarea>
                        <div style="display: flex; gap: 6px;"><button type="submit" class="btn-salva" style="flex:1;">Salva</button><button type="button" onclick="nascondiModifica('scheda', {s_id})" style="flex:1; background: rgba(255,255,255,0.1); color:#fff; border:none; border-radius:8px; font-weight:bold; cursor:pointer; font-size:11px;">Annulla</button></div>
                    </form>
                </div>
            </div>
            """

    # --- Cucina HTML ---
    lista_ricette_html = ""
    if not ricette_items:
        lista_ricette_html = "<div style='text-align: center; padding: 25px; color: #64748b; font-size: 12px; letter-spacing: 2px;'>// NESSUNA RICETTA IN ARCHIVIO //</div>"
    else:
        for r in ricette_items:
            r_id, r_titolo, r_cat, r_utensili, r_ingr, r_proc = r[0], r[1], r[2], r[3], r[4], r[5]
            
            ingr_li = ""
            for idx, ing in enumerate([i.strip() for i in r_ingr.split(",") if i.strip()]):
                ing_id = f"ricetta_{r_id}_{idx}"
                ingr_li += f"""
                <li style="margin-bottom: 4px; display: flex; align-items: center; justify-content: space-between;">
                    <span id="txt_{ing_id}" style="color: #f8fafc; font-size: 12px;">{ing}</span>
                    <button type="button" onclick="toggleArticolo('{ing_id}')" id="btn_{ing_id}" style="width: 18px; height: 18px; border-radius: 4px; border: 2px solid var(--accent-color); background: transparent; color: var(--bg-color); font-weight: bold; cursor: pointer; display: flex; align-items: center; justify-content: center; font-size: 9px;"></button>
                </li>
                """
            
            lista_ricette_html += f"""
            <div class="cyber-card" style="margin-bottom: 14px; border-left: 4px solid #f59e0b;">
                <div id="view_ricetta_{r_id}">
                    <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 6px;">
                        <div style="font-size: 15px; font-weight: 700; color: #ffffff;">🍳 {r_titolo}</div>
                        <div style="display: flex; gap: 6px;">
                            <button type="button" onclick="mostraModifica('ricetta', {r_id})" style="background: rgba(245,158,11,0.1); color: #f59e0b; border: 1px solid rgba(245,158,11,0.3); padding: 4px 8px; border-radius: 6px; cursor: pointer; font-size: 11px;">✏️</button>
                            <form action="/elimina_ricetta/{r_id}" method="post" style="margin: 0;"><button type="submit" style="background: rgba(244, 63, 94, 0.1); color: #f43f5e; border: 1px solid rgba(244, 63, 94, 0.3); padding: 4px 8px; border-radius: 6px; cursor: pointer; font-size: 11px;">🗑️</button></form>
                        </div>
                    </div>
                    <span style="background: rgba(245, 158, 11, 0.15); color: #f59e0b; padding: 2px 6px; border-radius: 4px; font-weight: 800; font-size: 9px; text-transform: uppercase;">{r_cat}</span>
                    
                    <div style="margin-top: 8px; background: rgba(15, 23, 42, 0.5); padding: 8px; border-radius: 8px; border: 1px dashed rgba(245, 158, 11, 0.3);">
                        <div style="color: #f59e0b; font-size: 10px; font-weight: 800; text-transform: uppercase; margin-bottom: 4px;">🛠️ Utensili Necessari</div>
                        <div style="color: #cbd5e1; font-size: 12px;">{r_utensili}</div>
                    </div>

                    <div style="margin-top: 8px; background: rgba(15, 23, 42, 0.5); padding: 8px; border-radius: 8px; border: 1px dashed rgba(56, 189, 248, 0.3);">
                        <div style="color: var(--accent-color); font-size: 10px; font-weight: 800; text-transform: uppercase; margin-bottom: 4px;">🥕 Ingredienti</div>
                        <ul style="list-style: none; padding: 0; margin: 0;">{ingr_li}</ul>
                    </div>

                    <div style="margin-top: 8px; color: #cbd5e1; font-size: 12px; background: rgba(5,7,12,0.5); padding: 8px; border-radius: 8px;">
                        <div style="color: #64748b; font-size: 10px; font-weight: 800; text-transform: uppercase; margin-bottom: 2px;">📖 Procedimento</div>
                        {r_proc}
                    </div>
                </div>

                <div id="edit_ricetta_{r_id}" style="display: none;">
                    <form action="/modifica_ricetta/{r_id}#tab-cucina" method="post">
                        <div style="font-size: 12px; font-weight: 900; color: #f59e0b; margin-bottom: 8px; text-transform: uppercase;">✏️ Modifica Ricetta</div>
                        <label>Titolo</label><input type="text" name="titolo" value="{r_titolo}" required>
                        <label>Categoria</label>
                        <select name="categoria">
                            <option value="Primo Piatto" {'selected' if r_cat=='Primo Piatto' else ''}>🍝 Primo Piatto</option>
                            <option value="Secondo Piatto" {'selected' if r_cat=='Secondo Piatto' else ''}>🥩 Secondo Piatto</option>
                            <option value="Dolce / Dessert" {'selected' if r_cat=='Dolce / Dessert' else ''}>🍰 Dolce / Dessert</option>
                            <option value="Altro" {'selected' if r_cat=='Altro' else ''}>🥗 Altro / Snack</option>
                        </select>
                        <label>Utensili</label><input type="text" name="utensili" value="{r_utensili}" required>
                        <label>Ingredienti</label><textarea name="ingredienti" rows="3" required>{r_ingr}</textarea>
                        <label>Procedimento</label><textarea name="procedimento" rows="4" required>{r_proc}</textarea>
                        <div style="display: flex; gap: 6px;"><button type="submit" class="btn-salva" style="flex:1;">Salva</button><button type="button" onclick="nascondiModifica('ricetta', {r_id})" style="flex:1; background: rgba(255,255,255,0.1); color:#fff; border:none; border-radius:8px; font-weight:bold; cursor:pointer; font-size:11px;">Annulla</button></div>
                    </form>
                </div>
            </div>
            """

    html_content = f"""
    <!DOCTYPE html>
    <html lang="it">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Cyber Suite</title>
        <link rel="icon" href="data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><text y=%22.9em%22 font-size=%2290%22>⚡</text></svg>">
        <style>
            :root {{
                --bg-color: #05070c;
                --panel-bg: rgba(11, 17, 32, 0.9);
                --accent-color: #38bdf8;
                --accent-border: rgba(56, 189, 248, 0.3);
                --accent-glow: rgba(56, 189, 248, 0.5);
                --gradient-start: #1e1b4b;
            }}
            body.theme-matrix {{
                --bg-color: #020c05;
                --panel-bg: rgba(6, 20, 10, 0.9);
                --accent-color: #22c55e;
                --accent-border: rgba(34, 197, 94, 0.3);
                --accent-glow: rgba(34, 197, 94, 0.5);
                --gradient-start: #052e16;
            }}
            body.theme-synthwave {{
                --bg-color: #09050c;
                --panel-bg: rgba(20, 11, 32, 0.9);
                --accent-color: #ec4899;
                --accent-border: rgba(236, 72, 153, 0.3);
                --accent-glow: rgba(236, 72, 153, 0.5);
                --gradient-start: #581c87;
            }}
            /* --- 3 NUOVI TEMI EXTRA --- */
            body.theme-cyberpunk {{
                --bg-color: #0d0221;
                --panel-bg: rgba(25, 9, 51, 0.9);
                --accent-color: #00ffcc;
                --accent-border: rgba(255, 0, 127, 0.4);
                --accent-glow: rgba(255, 0, 127, 0.6);
                --gradient-start: #3b0764;
            }}
            body.theme-oled {{
                --bg-color: #000000;
                --panel-bg: rgba(10, 10, 10, 0.95);
                --accent-color: #ffffff;
                --accent-border: rgba(255, 255, 255, 0.2);
                --accent-glow: rgba(255, 255, 255, 0.3);
                --gradient-start: #111111;
            }}
            body.theme-sunset {{
                --bg-color: #1a0b2e;
                --panel-bg: rgba(43, 16, 85, 0.85);
                --accent-color: #ff9e00;
                --accent-border: rgba(255, 94, 98, 0.4);
                --accent-glow: rgba(255, 94, 98, 0.5);
                --gradient-start: #4a154b;
            }}

            * {{ box-sizing: border-box; }}
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background-color: var(--bg-color);
                background-image: 
                    radial-gradient(circle at 50% 0%, var(--gradient-start) 0%, var(--bg-color) 70%),
                    linear-gradient(rgba(56, 189, 248, 0.03) 1px, transparent 1px),
                    linear-gradient(90deg, rgba(56, 189, 248, 0.03) 1px, transparent 1px);
                background-size: 100% 100%, 20px 20px, 20px 20px;
                margin: 0; padding: 16px; color: #cbd5e1; min-height: 100vh;
                transition: background 0.3s ease;
            }}
            .container {{
                max-width: 500px; margin: 0 auto;
                background: var(--panel-bg);
                backdrop-filter: blur(25px);
                padding: 20px; border-radius: 24px;
                border: 1px solid var(--accent-border);
                box-shadow: 0 0 40px rgba(0, 0, 0, 0.9);
            }}
            .header {{ text-align: center; margin-bottom: 12px; position: relative; }}
            .header h2 {{
                color: #ffffff; margin: 0 0 4px 0; font-size: 24px; font-weight: 900;
                letter-spacing: 2px; text-shadow: 0 0 15px var(--accent-glow);
            }}
            .header p {{ color: var(--accent-color); margin: 0; font-size: 9px; text-transform: uppercase; letter-spacing: 3px; opacity: 0.8; }}
            
            .top-dashboard {{ display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-bottom: 14px; }}
            .dashboard-box {{ background: rgba(15, 23, 42, 0.7); padding: 10px; border-radius: 12px; border: 1px solid var(--accent-border); display: flex; flex-direction: column; justify-content: center; align-items: center; text-align: center; }}
            .dashboard-box label {{ font-size: 8px; color: #64748b; margin-bottom: 4px; text-transform: uppercase; letter-spacing: 1px; }}
            .weather-content {{ font-size: 12px; font-weight: 700; color: #f8fafc; }}
            .theme-selector {{ background: rgba(5, 7, 12, 0.9); border: 1px solid var(--accent-border); color: var(--accent-color); padding: 4px 8px; border-radius: 6px; font-size: 11px; font-weight: 800; cursor: pointer; text-transform: uppercase; outline: none; width: 100%; text-align: center; }}

            .nav-tabs {{
                display: flex; gap: 3px; background: rgba(15, 23, 42, 0.9);
                padding: 4px; border-radius: 12px; margin-bottom: 16px;
                border: 1px solid var(--accent-border); overflow-x: auto;
            }}
            .tab-btn {{
                flex: 1; background: transparent; border: none; color: #64748b;
                padding: 8px 4px; border-radius: 8px; font-size: 9px; font-weight: 800;
                cursor: pointer; text-transform: uppercase; text-align: center; text-decoration: none;
                white-space: nowrap; transition: all 0.2s; letter-spacing: 0.5px;
            }}
            .tab-btn.active {{
                background: var(--accent-color); color: var(--bg-color);
                box-shadow: 0 0 15px var(--accent-glow);
            }}
            
            .section-content {{ display: none; }}
            .section-content.active {{ display: block; }}

            .stats-box {{
                display: flex; justify-content: space-between;
                background: rgba(15, 23, 42, 0.7); padding: 10px 14px;
                border-radius: 10px; margin-bottom: 14px;
                border: 1px solid var(--accent-border);
                font-size: 11px; font-weight: 700; color: #64748b; letter-spacing: 1px;
            }}
            .stats-box span {{ color: var(--accent-color); text-shadow: 0 0 8px var(--accent-glow); }}

            .filters {{ display: flex; gap: 6px; margin-bottom: 14px; overflow-x: auto; padding-bottom: 4px; }}
            .filter-btn {{
                background: rgba(15, 23, 42, 0.8); border: 1px solid var(--accent-border);
                color: #64748b; padding: 6px 10px; border-radius: 8px; font-size: 10px;
                font-weight: 800; cursor: pointer; white-space: nowrap; text-transform: uppercase; letter-spacing: 1px;
            }}
            .filter-btn.active {{ background: var(--accent-color); color: var(--bg-color); border-color: var(--accent-color); box-shadow: 0 0 10px var(--accent-glow); }}

            .card-form {{
                background: rgba(15, 23, 42, 0.6); padding: 16px; border-radius: 16px;
                border: 1px solid var(--accent-border); margin-bottom: 16px;
                box-shadow: inset 0 0 15px rgba(0,0,0,0.5); position: relative;
            }}
            .card-form h3 {{
                color: var(--accent-color); font-size: 12px; margin: 0 0 12px 0; font-weight: 900;
                text-transform: uppercase; letter-spacing: 1.5px; text-shadow: 0 0 8px var(--accent-glow);
            }}
            label {{ font-size: 9px; font-weight: 800; color: #64748b; display: block; margin-bottom: 4px; text-transform: uppercase; letter-spacing: 1.5px; }}
            input, select, textarea {{
                width: 100%; padding: 10px 12px; margin-bottom: 12px;
                border: 1px solid var(--accent-border); border-radius: 8px;
                font-size: 13px; background: rgba(5, 7, 12, 0.9); color: #ffffff; outline: none;
                transition: all 0.2s;
            }}
            input:focus, select:focus, textarea:focus {{
                border-color: var(--accent-color); box-shadow: 0 0 15px var(--accent-glow);
                background: var(--bg-color);
            }}
            select option {{ background: #05070c; color: #fff; }}
            
            button.btn-salva {{
                background: linear-gradient(135deg, var(--accent-color) 0%, #0284c7 100%);
                color: var(--bg-color); border: none; padding: 12px; width: 100%;
                border-radius: 8px; font-size: 13px; font-weight: 900; cursor: pointer;
                text-transform: uppercase; letter-spacing: 1.5px;
                box-shadow: 0 0 20px var(--accent-glow); transition: all 0.2s;
            }}
            button.btn-salva:hover {{ box-shadow: 0 0 30px var(--accent-glow); }}

            .search-box {{
                width: 100%; padding: 10px 14px; margin-bottom: 12px; border-radius: 10px;
                border: 1px solid var(--accent-border); background: rgba(5, 7, 12, 0.9);
                color: #fff; font-size: 13px; outline: none;
            }}
            .section-title {{
                color: #ffffff; font-size: 12px; font-weight: 900; margin: 16px 0 10px 0;
                text-transform: uppercase; letter-spacing: 1.5px; text-shadow: 0 0 10px rgba(255,255,255,0.2);
            }}

            .cyber-card {{
                background: rgba(15, 23, 42, 0.7); backdrop-filter: blur(10px);
                padding: 14px; border-radius: 12px; border: 1px solid var(--accent-border);
                box-shadow: 0 4px 20px rgba(0,0,0,0.5);
            }}

            .cyber-flyer-box {{
                background: linear-gradient(135deg, rgba(15, 23, 42, 0.95) 0%, rgba(20, 27, 45, 0.9) 100%);
                border: 1px solid rgba(251, 191, 36, 0.5); border-radius: 18px; padding: 18px;
                margin-bottom: 20px; box-shadow: 0 0 30px rgba(251, 191, 36, 0.15);
                position: relative; overflow: hidden;
            }}
            .cyber-flyer-box::before {{
                content: ''; position: absolute; top: 0; left: 0; width: 4px; height: 100%;
                background: inherit; box-shadow: inherit;
            }}
            .cyber-flyer-title {{
                font-size: 12px; font-weight: 900; text-transform: uppercase;
                letter-spacing: 2px; margin-bottom: 12px; display: flex; align-items: center; gap: 8px;
            }}
            .cyber-btn {{
                color: var(--bg-color); border: none; padding: 12px; width: 100%; border-radius: 10px;
                font-size: 12px; font-weight: 900; cursor: pointer; text-transform: uppercase;
                letter-spacing: 1.5px; transition: all 0.2s;
            }}

            #suggerimenti-box {{
                position: absolute; top: 70px; left: 16px; right: 16px; background: #0b1120;
                border: 1px solid var(--accent-color); border-radius: 8px; box-shadow: 0 10px 30px rgba(0,0,0,0.9);
                z-index: 100; display: none; overflow: hidden;
            }}
            .sugg-item {{
                padding: 10px 12px; border-bottom: 1px solid rgba(56, 189, 248, 0.2); cursor: pointer;
                display: flex; justify-content: space-between; align-items: center; transition: 0.2s;
            }}
            .sugg-item:hover {{ background: rgba(56, 189, 248, 0.15); }}
        </style>
        <script>
            function switchTab(tabId, btn) {{
                document.querySelectorAll('.section-content').forEach(el => el.classList.remove('active'));
                document.querySelectorAll('.tab-btn').forEach(el => el.classList.remove('active'));
                document.getElementById(tabId).classList.add('active');
                if(btn) btn.classList.add('active');
                history.replaceState(null, null, '#' + tabId);
            }}

            window.onload = function() {{
                let hash = window.location.hash.replace('#', '');
                if (hash && document.getElementById(hash)) {{
                    let btn = document.querySelector(`[onclick*="${{hash}}"]`);
                    switchTab(hash, btn);
                }}
                caricaMeteo();
                caricaTemaSalvato();
            }};

            function mostraModifica(tipo, id) {{
                document.getElementById('view_' + tipo + '_' + id).style.display = 'none';
                document.getElementById('edit_' + tipo + '_' + id).style.display = 'block';
            }}
            function nascondiModifica(tipo, id) {{
                document.getElementById('view_' + tipo + '_' + id).style.display = 'block';
                document.getElementById('edit_' + tipo + '_' + id).style.display = 'none';
            }}

            async function caricaMeteo() {{
                try {{
                    let res = await fetch('https://api.open-meteo.com/v1/forecast?latitude=38.14&longitude=15.21&current=temperature_2m,weather_code');
                    let data = await res.json();
                    let temp = Math.round(data.current.temperature_2m);
                    let code = data.current.weather_code;
                    let icona = '🌤️';
                    if (code === 0) icona = '☀️';
                    else if (code >= 1 && code <= 3) icona = '⛅';
                    else if (code >= 51 && code <= 67) icona = '🌧️';
                    document.getElementById('weather-widget').innerHTML = `${{icona}} Barcellona P.G.<br><b style="font-size:14px; color:var(--accent-color);">${{temp}}°C</b>`;
                }} catch(e) {{
                    document.getElementById('weather-widget').innerHTML = '🌤️ Barcellona P.G.<br><b style="font-size:14px; color:var(--accent-color);">16°C</b>';
                }}
            }}

            function cambiaTema(tema) {{
                document.body.className = '';
                if (tema !== 'default') document.body.classList.add('theme-' + tema);
                localStorage.setItem('cyber_theme', tema);
            }}
            function caricaTemaSalvato() {{
                let salvato = localStorage.getItem('cyber_theme') || 'cyberpunk';
                document.getElementById('theme-switcher').value = salvato;
                cambiaTema(salvato);
            }}

            // --- Timer Focus ---
            let timerInterval = null;
            let timeLeft = 25 * 60;
            let isRunning = false;

            function formatTime(seconds) {{
                let m = Math.floor(seconds / 60);
                let s = seconds % 60;
                return `${{m < 10 ? '0' : ''}}${{m}}:${{s < 10 ? '0' : ''}}${{s}}`;
            }}

            function togglePomodoroTimer() {{
                let btn = document.getElementById('pomodoro-toggle-btn');
                if (isRunning) {{
                    clearInterval(timerInterval);
                    isRunning = false;
                    btn.innerHTML = '⚡ Avvia Focus';
                }} else {{
                    isRunning = true;
                    btn.innerHTML = '⏸️ Pausa';
                    timerInterval = setInterval(() => {{
                        if (timeLeft > 0) {{
                            timeLeft--;
                            document.getElementById('pomodoro-timer-display').innerText = formatTime(timeLeft);
                        }} else {{
                            clearInterval(timerInterval);
                            isRunning = false;
                            alert('Sessione Pomodoro completata!');
                            resetPomodoro(25 * 60);
                        }}
                    }}, 1000);
                }}
            }}

            function setPomodoroMode(minutes) {{
                clearInterval(timerInterval);
                isRunning = false;
                document.getElementById('pomodoro-toggle-btn').innerHTML = '⚡ Avvia Focus';
                timeLeft = minutes * 60;
                document.getElementById('pomodoro-timer-display').innerText = formatTime(timeLeft);
            }}

            function applicaCustomTimer() {{
                let min = parseInt(document.getElementById('custom-min-input').value);
                if (min && min > 0) {{
                    setPomodoroMode(min);
                }} else {{
                    alert('Inserisci un numero valido di minuti!');
                }}
            }}

            function resetPomodoro(seconds = 25 * 60) {{
                clearInterval(timerInterval);
                isRunning = false;
                timeLeft = seconds;
                document.getElementById('pomodoro-timer-display').innerText = formatTime(timeLeft);
                document.getElementById('pomodoro-toggle-btn').innerHTML = '⚡ Avvia Focus';
            }}

            // --- Timer Allenamento Personalizzabile & Cronometro ---
            let allenamentoInterval = null;
            let allenamentoTimeLeft = 0;
            let allenamentoRunning = false;

            function avviaTimerAllenamentoCustom() {{
                let inputVal = parseInt(document.getElementById('allenamento-custom-input').value);
                if (!inputVal || inputVal <= 0) {{
                    alert('Inserisci un numero valido di minuti!');
                    return;
                }}
                clearInterval(allenamentoInterval);
                allenamentoTimeLeft = inputVal * 60;
                allenamentoRunning = true;
                document.getElementById('allenamento-timer-display').innerText = formatTime(allenamentoTimeLeft);
                
                allenamentoInterval = setInterval(() => {{
                    if (allenamentoTimeLeft > 0) {{
                        allenamentoTimeLeft--;
                        document.getElementById('allenamento-timer-display').innerText = formatTime(allenamentoTimeLeft);
                    }} else {{
                        clearInterval(allenamentoInterval);
                        allenamentoRunning = false;
                        alert('🏋️‍♂️ Tempo di allenamento scaduto!');
                        document.getElementById('allenamento-timer-display').innerText = "00:00";
                    }}
                }}, 1000);
            }}

            function fermaTimerAllenamento() {{
                clearInterval(allenamentoInterval);
                allenamentoRunning = false;
                document.getElementById('allenamento-timer-display').innerText = "00:00";
            }}

            // Cronometro Allenamento
            let cronoInterval = null;
            let cronoSeconds = 0;
            let cronoRunning = false;

            function toggleCronometro() {{
                let btn = document.getElementById('crono-toggle-btn');
                if (cronoRunning) {{
                    clearInterval(cronoInterval);
                    cronoRunning = false;
                    btn.innerHTML = '▶️ Avvia Crono';
                }} else {{
                    cronoRunning = true;
                    btn.innerHTML = '⏸️ Pausa';
                    cronoInterval = setInterval(() => {{
                        cronoSeconds++;
                        document.getElementById('cronometro-display').innerText = formatTime(cronoSeconds);
                    }}, 1000);
                }}
            }}

            function resetCronometro() {{
                clearInterval(cronoInterval);
                cronoRunning = false;
                cronoSeconds = 0;
                document.getElementById('cronometro-display').innerText = "00:00";
                document.getElementById('crono-toggle-btn').innerHTML = '▶️ Avvia Crono';
            }}

            // --- Multi-Timer Dinamico Cucina ---
            let activeTimers = [];

            function aggiungiMultiTimerCucina() {{
                let nome = document.getElementById('cucina-timer-nome').value.trim() || 'Timer Cucina';
                let minuti = parseInt(document.getElementById('cucina-timer-minuti').value);
                if (!minuti || minuti <= 0) {{
                    alert('Inserisci minuti validi per il timer!');
                    return;
                }}
                let totalSec = minuti * 60;
                let timerId = Date.now();

                let container = document.getElementById('lista-multi-timers');
                let box = document.createElement('div');
                box.id = `timer_box_${{timerId}}`;
                box.style.cssText = "background: rgba(15,23,42,0.8); border: 1px solid rgba(245,158,11,0.4); padding: 8px 12px; border-radius: 8px; margin-bottom: 6px; display: flex; justify-content: space-between; align-items: center;";
                
                box.innerHTML = `
                    <div>
                        <div style="color: #f59e0b; font-weight: bold; font-size: 12px;">⏰ ${{nome}}</div>
                        <div id="countdown_${{timerId}}" style="color: #fff; font-size: 18px; font-family: monospace;">${{formatTime(totalSec)}}</div>
                    </div>
                    <button type="button" onclick="rimuoviMultiTimer(${{timerId}})" style="background: rgba(244,63,94,0.2); color: #f43f5e; border: 1px solid #f43f5e; padding: 4px 8px; border-radius: 4px; font-size: 10px; cursor: pointer;">Elimina</button>
                `;
                container.prepend(box);

                let interval = setInterval(() => {{
                    if (totalSec > 0) {{
                        totalSec--;
                        let el = document.getElementById(`countdown_${{timerId}}`);
                        if (el) el.innerText = formatTime(totalSec);
                    }} else {{
                        clearInterval(interval);
                        alert(`🔥 Timer "${{nome}}" scaduto! Pronto!`);
                    }}
                }}, 1000);

                activeTimers.push({{ id: timerId, interval: interval }});
                document.getElementById('cucina-timer-nome').value = '';
            }}

            function rimuoviMultiTimer(timerId) {{
                let obj = activeTimers.find(t => t.id === timerId);
                if (obj) {{
                    clearInterval(obj.interval);
                    activeTimers = activeTimers.filter(t => t.id !== timerId);
                }}
                let box = document.getElementById(`timer_box_${{timerId}}`);
                if (box) box.remove();
            }}

            function toggleArticolo(artId) {{
                let txt = document.getElementById('txt_' + artId);
                let btn = document.getElementById('btn_' + artId);
                if (txt.style.textDecoration === 'line-through') {{
                    txt.style.textDecoration = 'none'; txt.style.opacity = '1'; btn.style.background = 'transparent'; btn.innerHTML = '';
                }} else {{
                    txt.style.textDecoration = 'line-through'; txt.style.opacity = '0.4'; btn.style.background = 'var(--accent-color)'; btn.innerHTML = '✓';
                }}
            }}

            function cercaVolantino() {{
                let negozio = document.getElementById('input-negozio-volantino').value.trim();
                if (negozio) window.open(`https://www.google.com/search?q=volantino+${{encodeURIComponent(negozio)}}`, '_blank');
                else alert('Inserisci il nome di un negozio!');
            }}

            let timeoutRicerca = null;
            async function cercaMediaAutocompletamento(query) {{
                let box = document.getElementById('suggerimenti-box');
                if(query.length < 3) {{ box.style.display = 'none'; return; }}
                clearTimeout(timeoutRicerca);
                timeoutRicerca = setTimeout(async () => {{
                    try {{
                        let html = '';
                        let resFilm = await fetch(`https://itunes.apple.com/search?term=${{encodeURIComponent(query)}}&media=movie&entity=movie&limit=3`);
                        let dataFilm = await resFilm.json();
                        dataFilm.results.forEach(item => {{
                            html += `<div class="sugg-item" onclick="selezionaMedia('${{item.trackName.replace(/'/g, "\\\\'") }}', '${{item.primaryGenreName || 'Generico'}}', 'Film')"><strong style="color:#fff;">${{item.trackName}}</strong><span style="font-size:9px; color:var(--accent-color);">🎬 Film</span></div>`;
                        }});
                        let resTv = await fetch(`https://api.tvmaze.com/search/shows?q=${{encodeURIComponent(query)}}`);
                        let dataTv = await resTv.json();
                        dataTv.slice(0, 3).forEach(item => {{
                            let show = item.show;
                            let gen = (show.genres && show.genres.length > 0) ? show.genres[0] : 'Generico';
                            html += `<div class="sugg-item" onclick="selezionaMedia('${{show.name.replace(/'/g, "\\\\'") }}', '${{gen}}', 'Serie TV')"><strong style="color:#fff;">${{show.name}}</strong><span style="font-size:9px; color:#a855f7;">📺 Serie TV</span></div>`;
                        }});
                        box.innerHTML = html; box.style.display = html ? 'block' : 'none';
                    }} catch(e) {{}}
                }}, 450);
            }}

            function selezionaMedia(titolo, genere, tipo) {{
                document.getElementById('input-titolo-media').value = titolo;
                document.getElementById('input-genere-media').value = genere;
                document.getElementById('select-tipo-media').value = tipo;
                document.getElementById('suggerimenti-box').style.display = 'none';
            }}

            async function generaOracolo() {{
                let box = document.getElementById('oracolo-results');
                box.innerHTML = '<div style="color: #a855f7; font-size: 11px; text-align: center;">Analisi neurale in corso...</div>';
                let topGenres = [];
                document.querySelectorAll('.media-card').forEach(card => {{
                    if (card.getAttribute('data-stato') === 'Completato' && parseInt(card.getAttribute('data-voto')) >= 4) {{
                        topGenres.push(card.getAttribute('data-genere'));
                    }}
                }});
                if (topGenres.length === 0) {{
                    box.innerHTML = '<div style="color: #94a3b8; font-size: 11px; text-align: center; margin-top: 10px;">Valuta (4-5 stelle) qualche titolo completato.</div>';
                    return;
                }}
                let randomGenre = topGenres[Math.floor(Math.random() * topGenres.length)];
                try {{
                    let res = await fetch(`https://itunes.apple.com/search?term=movie+${{encodeURIComponent(randomGenre)}}&limit=10&media=all`);
                    let data = await res.json();
                    let html = `<div style="color: #cbd5e1; font-size: 11px; margin-top: 10px; margin-bottom: 8px;">Affinità per: <b>${{randomGenre}}</b></div>`;
                    data.results.filter(i => i.kind === 'feature-movie' || i.collectionType === 'TV Season').slice(0, 3).forEach(item => {{
                        let titolo = item.trackName || item.collectionName;
                        html += `
                        <div style="background: rgba(15,23,42,0.6); border: 1px solid rgba(168, 85, 247, 0.2); border-radius: 8px; padding: 10px; margin-bottom: 8px; display: flex; justify-content: space-between; align-items: center;">
                            <div><div style="color: #f8fafc; font-weight: 700; font-size: 13px;">${{titolo}}</div></div>
                            <button type="button" onclick="window.open('https://www.google.com/search?q=dove+guardare+${{encodeURIComponent(titolo)}}', '_blank')" style="background: rgba(168, 85, 247, 0.15); color: #a855f7; border: 1px solid rgba(168, 85, 247, 0.4); border-radius: 6px; padding: 6px 10px; font-size: 10px; font-weight: bold; cursor: pointer;">🔍 Streaming</button>
                        </div>`;
                    }});
                    box.innerHTML = html;
                }} catch(e) {{ box.innerHTML = '<div style="color: #f43f5e; font-size: 11px; text-align: center;">Errore server esterni.</div>'; }}
            }}

            let filtroCorrente = 'tutti';
            let testoRicerca = '';
            function applicaFiltri() {{
                let cards = document.getElementsByClassName('evento-card');
                for (let card of cards) {{
                    let match = card.getAttribute('data-titolo').includes(testoRicerca);
                    let stato = card.getAttribute('data-stato');
                    let prio = card.getAttribute('data-prio');
                    let matchFiltro = true;
                    if (filtroCorrente === 'urgente') matchFiltro = (prio === 'urgente');
                    else if (filtroCorrente === 'incompleto') matchFiltro = (stato === 'incompleto');
                    else if (filtroCorrente === 'completato') matchFiltro = (stato === 'completato');
                    card.style.display = (match && matchFiltro) ? "block" : "none";
                }}
            }}
            function filtraTesto(val) {{ testoRicerca = val.toLowerCase(); applicaFiltri(); }}
            function impostaFiltro(tipo, btn) {{
                filtroCorrente = tipo;
                document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                applicaFiltri();
            }}
        </script>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h2>⚡ CYBER SUITE</h2>
                <p>Neural Command Center v9.0</p>
            </div>

            <!-- DASHBOARD ALTO -->
            <div class="top-dashboard">
                <div class="dashboard-box">
                    <label>Stazione Meteo</label>
                    <div class="weather-content" id="weather-widget">🛰️ Connessione...</div>
                </div>
                <div class="dashboard-box">
                    <label>Interfaccia Tema</label>
                    <select id="theme-switcher" class="theme-selector" onchange="cambiaTema(this.value)">
                        <option value="cyberpunk">⚡ Cyberpunk Neon</option>
                        <option value="matrix">💻 Matrix Green</option>
                        <option value="synthwave">🌆 Synthwave</option>
                        <option value="oled">🖤 OLED Minimal</option>
                        <option value="sunset">🌅 Sunset Synthwave</option>
                    </select>
                </div>
            </div>

            <!-- MENU TAB -->
            <div class="nav-tabs">
                <button class="tab-btn active" onclick="switchTab('tab-agenda', this)">📅 Agenda</button>
                <button class="tab-btn" onclick="switchTab('tab-spesa', this)">🛒 Spesa</button>
                <button class="tab-btn" onclick="switchTab('tab-misure', this)">📐 Misure</button>
                <button class="tab-btn" onclick="switchTab('tab-media', this)">🎬 Film & TV</button>
                <button class="tab-btn" onclick="switchTab('tab-focus', this)">⚡ Focus</button>
                <button class="tab-btn" onclick="switchTab('tab-allenamento', this)">🏋️‍♂️ Allenamento</button>
                <button class="tab-btn" onclick="switchTab('tab-armadio', this)">🧥 Armadio</button>
                <button class="tab-btn" onclick="switchTab('tab-cucina', this)">🍳 Cucina</button>
            </div>

            <!-- SEZIONE AGENDA -->
            <div id="tab-agenda" class="section-content active">
                <div class="stats-box">
                    <div>Totale: <span>{totale_eventi}</span></div>
                    <div>Completati: <span>{completati_eventi}/{totale_eventi}</span></div>
                </div>
                <div class="card-form">
                    <form action="/aggiungi_evento#tab-agenda" method="post">
                        <h3>➕ Inserisci Evento</h3>
                        <label>Oggetto</label><input type="text" name="titolo" placeholder="es. Protocollo Alpha" required>
                        <label>Data e Ora</label><input type="datetime-local" name="data_ora" required>
                        <label>Priorità</label>
                        <select name="priorita">
                            <option value="Ordinario">⚡ Ordinario</option>
                            <option value="Urgente">🔥 Urgente / Critico</option>
                            <option value="Bassa">💤 Bassa Priorità</option>
                        </select>
                        <label>Dettagli</label><input type="text" name="descrizione" placeholder="Cifratura richiesta">
                        <button type="submit" class="btn-salva">Esegui Salvataggio</button>
                    </form>
                </div>
                <input type="text" class="search-box" placeholder="🔍 Cerca nel database..." onkeyup="filtraTesto(this.value)">
                <div class="filters">
                    <button class="filter-btn active" onclick="impostaFiltro('tutti', this)">Tutti</button>
                    <button class="filter-btn" onclick="impostaFiltro('incompleto', this)">In Sospeso</button>
                    <button class="filter-btn" onclick="impostaFiltro('urgente', this)">🔥 Urgenti</button>
                    <button class="filter-btn" onclick="impostaFiltro('completato', this)">✓ Completati</button>
                </div>
                <div class="section-title"><span>🛡️ Database Attivo</span></div>
                <div id="lista-container">{lista_eventi_html}</div>
            </div>

            <!-- SEZIONE SPESA -->
            <div id="tab-spesa" class="section-content">
                <div class="cyber-flyer-box" style="border-color: rgba(251, 191, 36, 0.5);">
                    <div class="cyber-flyer-title" style="color: #fbbf24;"><span>📡</span> <span>Terminal Volantini Web</span></div>
                    <label style="color: #fbbf24; margin-bottom: 6px;">Cerca Negozio / Supermercato</label>
                    <input type="text" id="input-negozio-volantino" placeholder="es. Esselunga, Lidl, Conad..." style="border-color: rgba(251, 191, 36, 0.4); background: rgba(5, 7, 12, 0.9);">
                    <button type="button" class="cyber-btn" onclick="cercaVolantino()" style="background: linear-gradient(135deg, #fbbf24 0%, #d97706 100%);">⚡ Connetti al Volantino</button>
                </div>
                <div class="card-form">
                    <form action="/aggiungi_spesa#tab-spesa" method="post">
                        <h3>🛒 Nuovo Documento Spesa</h3>
                        <label>Titolo Documento</label><input type="text" name="titolo_documento" placeholder="es. Spesa della Settimana" required>
                        <label>Negozi e Articoli</label><textarea name="negozi_articoli" rows="5" placeholder="Esselunga: latte, pane&#10;Fruttivendolo: mele" required></textarea>
                        <button type="submit" class="btn-salva">Salva Documento Spesa</button>
                    </form>
                </div>
                <div class="section-title"><span>📋 Documenti Spesa Attivi</span></div>
                {lista_spesa_html}
            </div>

            <!-- SEZIONE MISURE -->
            <div id="tab-misure" class="section-content">
                <div class="card-form">
                    <form action="/aggiungi_misura#tab-misure" method="post">
                        <h3>📐 Nuova Scheda Misure</h3>
                        <label>1. Prodotto / Mobile</label><input type="text" name="prodotto" placeholder="es. Divano Salotto" required>
                        <label>2. Misure Tecniche</label>
                        <div style="display: flex; gap: 6px; margin-bottom: 8px;">
                            <select name="m1_tipo" style="flex:1; margin-bottom:0;"><option value="Altezza">Altezza</option><option value="Larghezza">Larghezza</option><option value="Profondità">Profondità</option></select>
                            <input type="text" name="m1_val" placeholder="es. 85 cm" style="flex:1; margin-bottom:0;" required>
                        </div>
                        <div style="display: flex; gap: 6px; margin-bottom: 8px;">
                            <select name="m2_tipo" style="flex:1; margin-bottom:0;"><option value="Larghezza">Larghezza</option><option value="Altezza">Altezza</option><option value="Profondità">Profondità</option></select>
                            <input type="text" name="m2_val" placeholder="es. 190 cm" style="flex:1; margin-bottom:0;">
                        </div>
                        <div style="display: flex; gap: 6px; margin-bottom: 12px;">
                            <select name="m3_tipo" style="flex:1; margin-bottom:0;"><option value="Profondità">Profondità</option><option value="Altezza">Altezza</option><option value="Larghezza">Larghezza</option></select>
                            <input type="text" name="m3_val" placeholder="es. 90 cm" style="flex:1; margin-bottom:0;">
                        </div>
                        <label>3. Materiale / Note Extra</label><input type="text" name="note_extra" placeholder="es. Tasselli, viti">
                        <button type="submit" class="btn-salva">Salva Scheda Misure</button>
                    </form>
                </div>
                <div class="section-title"><span>📂 Archivio Schede Misure</span></div>
                {lista_misure_html}
            </div>

            <!-- SEZIONE FILM & TV -->
            <div id="tab-media" class="section-content">
                <div class="cyber-flyer-box" style="border-color: rgba(168, 85, 247, 0.5);">
                    <div class="cyber-flyer-title" style="color: #a855f7;"><span>🔮</span> <span>Oracolo Suggerimenti & Piattaforme</span></div>
                    <p style="font-size: 11px; color: #94a3b8; margin-top: 0; margin-bottom: 12px;">Analisi dei titoli valutati 4 o 5 stelle.</p>
                    <button type="button" class="cyber-btn" onclick="generaOracolo()" style="background: linear-gradient(135deg, #a855f7 0%, #7e22ce 100%);">⚡ Avvia Analisi Neurale</button>
                    <div id="oracolo-results"></div>
                </div>
                <div class="card-form" style="position: relative;">
                    <form action="/aggiungi_media#tab-media" method="post">
                        <h3>🍿 Aggiungi Titolo</h3>
                        <label>Titolo Film / Serie TV</label><input type="text" name="titolo" id="input-titolo-media" placeholder="Digita per cercare..." onkeyup="cercaMediaAutocompletamento(this.value)" autocomplete="off" required>
                        <div id="suggerimenti-box"></div>
                        <div style="display: flex; gap: 10px;">
                            <div style="flex:1;"><label>Genere</label><input type="text" name="genere" id="input-genere-media" placeholder="es. Sci-Fi" required></div>
                            <div style="flex:1;"><label>Tipologia</label>
                                <select name="tipo" id="select-tipo-media"><option value="Film">🎬 Film</option><option value="Serie TV">📺 Serie TV</option></select>
                            </div>
                        </div>
                        <div style="display: flex; gap: 10px;">
                            <div style="flex:1;"><label>Stato</label><select name="stato"><option value="Da Vedere">⏳ Da Vedere</option><option value="In Corso">⚡ In Corso</option><option value="Completato">✓ Completato</option></select></div>
                            <div style="flex:1;"><label>Valutazione</label>
                                <select name="voto" style="font-family: monospace;">
                                    <option value="">Da valutare</option>
                                    <option value="5">⭐⭐⭐⭐⭐</option><option value="4">⭐⭐⭐⭐</option><option value="3">⭐⭐⭐</option><option value="2">⭐⭐</option><option value="1">⭐</option>
                                </select>
                            </div>
                        </div>
                        <button type="submit" class="btn-salva">Salva in Archivio</button>
                    </form>
                </div>
                <div class="section-title"><span>📼 Archivio Intrattenimento</span></div>
                {lista_media_html}
            </div>

            <!-- SEZIONE 5: POMODORO FOCUS -->
            <div id="tab-focus" class="section-content">
                <div class="cyber-card" style="text-align: center; padding: 20px; margin-bottom: 16px; border-left: 4px solid var(--accent-color);">
                    <div style="font-size: 10px; color: #64748b; font-weight: 800; text-transform: uppercase; letter-spacing: 2px; margin-bottom: 6px;">⏱️ Pomodoro Neural Timer</div>
                    <div id="pomodoro-timer-display" style="font-size: 42px; font-weight: 900; color: #ffffff; font-family: monospace; text-shadow: 0 0 20px var(--accent-glow); margin-bottom: 10px;">25:00</div>
                    
                    <div style="display: flex; gap: 6px; justify-content: center; margin-bottom: 10px;">
                        <button type="button" onclick="setPomodoroMode(25)" style="background: rgba(56,189,248,0.1); color: var(--accent-color); border: 1px solid var(--accent-border); padding: 5px 8px; border-radius: 6px; font-size: 10px; font-weight: bold; cursor: pointer;">25m</button>
                        <button type="button" onclick="setPomodoroMode(45)" style="background: rgba(56,189,248,0.1); color: var(--accent-color); border: 1px solid var(--accent-border); padding: 5px 8px; border-radius: 6px; font-size: 10px; font-weight: bold; cursor: pointer;">45m</button>
                        <button type="button" onclick="setPomodoroMode(5)" style="background: rgba(56,189,248,0.1); color: var(--accent-color); border: 1px solid var(--accent-border); padding: 5px 8px; border-radius: 6px; font-size: 10px; font-weight: bold; cursor: pointer;">5m Pausa</button>
                        <button type="button" onclick="resetPomodoro(25*60)" style="background: rgba(244,63,94,0.1); color: #f43f5e; border: 1px solid rgba(244,63,94,0.3); padding: 5px 8px; border-radius: 6px; font-size: 10px; font-weight: bold; cursor: pointer;">Reset</button>
                    </div>

                    <div style="display: flex; gap: 6px; justify-content: center; margin-bottom: 14px; max-width: 250px; margin-left: auto; margin-right: auto;">
                        <input type="number" id="custom-min-input" placeholder="Minuti custom" min="1" max="180" style="margin-bottom: 0; padding: 6px; font-size: 11px; text-align: center;">
                        <button type="button" onclick="applicaCustomTimer()" style="background: var(--accent-color); color: var(--bg-color); border: none; border-radius: 6px; padding: 6px 12px; font-size: 10px; font-weight: 900; cursor: pointer;">Imposta</button>
                    </div>

                    <button type="button" id="pomodoro-toggle-btn" class="btn-salva" onclick="togglePomodoroTimer()">⚡ Avvia Focus</button>
                </div>

                <div class="card-form">
                    <form action="/aggiungi_pomodoro#tab-focus" method="post">
                        <h3>🎯 Micro-Obiettivo Sessione</h3>
                        <label>Attività</label><input type="text" name="compito" placeholder="es. Scrivere codice server.py" required>
                        <label>Categoria / Etichetta</label>
                        <select name="categoria">
                            <option value="Studio">📚 Studio</option>
                            <option value="Lavoro">💻 Lavoro / Codice</option>
                            <option value="Personale">⚡ Personale</option>
                        </select>
                        <button type="submit" class="btn-salva">Aggiungi a Focus</button>
                    </form>
                </div>

                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                    <div class="section-title" style="margin: 0;"><span>📋 Obiettivi in Coda</span></div>
                    <form action="/pulisci_completati_pomodoro#tab-focus" method="post" style="margin:0;">
                        <button type="submit" style="background: rgba(244,63,94,0.1); color: #f43f5e; border: 1px solid rgba(244,63,94,0.3); padding: 4px 8px; border-radius: 6px; cursor: pointer; font-size: 10px; font-weight: bold;">🗑️ Pulisci Completati</button>
                    </form>
                </div>
                {lista_pomodoro_html}
            </div>

            <!-- SEZIONE 6: ALLENAMENTO & RECORD (CON TIMER PERSONALIZZABILE) -->
            <div id="tab-allenamento" class="section-content">
                <!-- TABELLA RECORD PERSONALI -->
                <div class="cyber-card" style="margin-bottom: 16px; border-left: 4px solid #22c55e;">
                    <div style="font-size: 13px; font-weight: 900; color: #22c55e; margin-bottom: 10px; text-transform: uppercase;">🏆 Tabella Record Personali (PR)</div>
                    {lista_record_html}
                    <form action="/aggiungi_record#tab-allenamento" method="post" style="margin-top: 12px; border-top: 1px solid rgba(34,197,94,0.2); padding-top: 10px;">
                        <div style="display: flex; gap: 6px;">
                            <input type="text" name="esercizio" placeholder="es. Squat / Panca / Corsa" style="flex:1; margin-bottom:6px; font-size:11px;" required>
                            <input type="text" name="peso_tempo" placeholder="es. 100 kg / 5 km" style="flex:1; margin-bottom:6px; font-size:11px;" required>
                        </div>
                        <button type="submit" style="background: rgba(34,197,94,0.2); color: #22c55e; border: 1px solid #22c55e; padding: 6px; border-radius: 6px; font-size: 10px; font-weight: bold; width: 100%; cursor: pointer;">+ Registra Record</button>
                    </form>
                </div>

                <!-- TIMER & CRONOMETRO ALLENAMENTO PERSONALIZZABILE -->
                <div class="cyber-card" style="text-align: center; padding: 16px; margin-bottom: 16px; border-left: 4px solid #22c55e;">
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px;">
                        <div>
                            <div style="font-size: 9px; color: #64748b; font-weight: 800; text-transform: uppercase; margin-bottom: 4px;">⏱️ Timer Sessione</div>
                            <div id="allenamento-timer-display" style="font-size: 28px; font-weight: 900; color: #fff; font-family: monospace; margin-bottom: 8px;">00:00</div>
                            <div style="display: flex; gap: 4px; margin-bottom: 6px;">
                                <input type="number" id="allenamento-custom-input" placeholder="Min" value="45" min="1" max="180" style="margin-bottom:0; font-size:11px; padding:4px; text-align:center;">
                            </div>
                            <div style="display: flex; gap: 4px;">
                                <button type="button" onclick="avviaTimerAllenamentoCustom()" style="background: rgba(34,197,94,0.2); color: #22c55e; border: 1px solid #22c55e; padding: 4px; border-radius: 4px; font-size: 9px; font-weight: bold; flex:1; cursor: pointer;">Avvia</button>
                                <button type="button" onclick="fermaTimerAllenamento()" style="background: rgba(244,63,94,0.1); color: #f43f5e; border: 1px solid rgba(244,63,94,0.3); padding: 4px; border-radius: 4px; font-size: 9px; font-weight: bold; flex:1; cursor: pointer;">Stop</button>
                            </div>
                        </div>
                        <div>
                            <div style="font-size: 9px; color: #64748b; font-weight: 800; text-transform: uppercase; margin-bottom: 4px;">⏱️ Cronometro</div>
                            <div id="cronometro-display" style="font-size: 28px; font-weight: 900; color: #fff; font-family: monospace; margin-bottom: 8px;">00:00</div>
                            <button type="button" id="crono-toggle-btn" onclick="toggleCronometro()" style="background: rgba(34,197,94,0.2); color: #22c55e; border: 1px solid #22c55e; padding: 6px; border-radius: 4px; font-size: 9px; font-weight: bold; width: 100%; cursor: pointer; margin-bottom: 4px;">▶️ Avvia</button>
                            <button type="button" onclick="resetCronometro()" style="background: rgba(255,255,255,0.1); color: #fff; border: none; padding: 4px; border-radius: 4px; font-size: 9px; font-weight: bold; width: 100%; cursor: pointer;">Reset</button>
                        </div>
                    </div>
                </div>

                <!-- SCHEDA DI ALLENAMENTO MODIFICABILE -->
                <div class="card-form">
                    <form action="/aggiungi_scheda#tab-allenamento" method="post">
                        <h3>📋 Inserisci Scheda di Allenamento</h3>
                        <label>Giorno / Tipologia</label><input type="text" name="giorno" placeholder="es. Lunedì - Petto & Tricipiti" required>
                        <label>Esercizi e Serie</label>
                        <textarea name="dettagli_esercizi" rows="4" placeholder="Panca piana 4x8 - 80kg&#10;Spinte manubri 3x10..." required></textarea>
                        <button type="submit" class="btn-salva" style="background: linear-gradient(135deg, #22c55e 0%, #15803d 100%);">Salva Scheda</button>
                    </form>
                </div>
                <div class="section-title"><span>📂 Le Tue Schede</span></div>
                {lista_schede_html}
            </div>

            <!-- SEZIONE 7: ARMADIO -->
            <div id="tab-armadio" class="section-content">
                <div class="card-form">
                    <form action="/aggiungi_capo#tab-armadio" method="post">
                        <h3>🧥 Aggiungi Capo al Guardaroba</h3>
                        <label>Nome / Modello Capo</label><input type="text" name="capo" placeholder="es. Felpa Oversize Nera" required>
                        <div style="display: flex; gap: 10px;">
                            <div style="flex:1;"><label>Categoria</label>
                                <select name="categoria">
                                    <option value="Felpe / Maglie">👕 Felpe / Maglie</option>
                                    <option value="Pantaloni">👖 Pantaloni</option>
                                    <option value="Scarpe">👟 Scarpe</option>
                                    <option value="Giacche">🧥 Giacche / Outerwear</option>
                                    <option value="Accessori">🧢 Accessori</option>
                                </select>
                            </div>
                            <div style="flex:1;"><label>Colore</label><input type="text" name="colore" placeholder="es. Nero Opaco" required></div>
                        </div>
                        <div style="display: flex; gap: 10px;">
                            <div style="flex:1;"><label>Stagione</label>
                                <select name="stagione">
                                    <option value="Autunno / Inverno">❄️ Autunno / Inverno</option>
                                    <option value="Primavera / Estate">☀️ Primavera / Estate</option>
                                    <option value="Quattro Stagioni">🔄 Quattro Stagioni</option>
                                </select>
                            </div>
                            <div style="flex:1;"><label>Posizione / Cassetto</label><input type="text" name="posizione" placeholder="es. Cassetto 2 / Appendiabiti" required></div>
                        </div>
                        <button type="submit" class="btn-salva">Registra nell'Armadio</button>
                    </form>
                </div>
                <div class="section-title"><span>📂 Archivio Guardaroba</span></div>
                {lista_armadio_html}
            </div>

            <!-- SEZIONE 8: CUCINA & MULTI-TIMER -->
            <div id="tab-cucina" class="section-content">
                <!-- MULTI-TIMER DINAMICO CUCINA -->
                <div class="cyber-card" style="padding: 16px; margin-bottom: 16px; border-left: 4px solid #f59e0b;">
                    <div style="font-size: 11px; color: #64748b; font-weight: 800; text-transform: uppercase; letter-spacing: 2px; margin-bottom: 8px;">⏱️ Multi-Timer Cucina Dinamico</div>
                    <div style="display: flex; gap: 6px; margin-bottom: 10px;">
                        <input type="text" id="cucina-timer-nome" placeholder="Nome (es. Pasta)" style="flex: 2; margin-bottom: 0; padding: 6px; font-size: 12px;">
                        <input type="number" id="cucina-timer-minuti" placeholder="Min" min="1" max="180" style="flex: 1; margin-bottom: 0; padding: 6px; font-size: 12px;">
                        <button type="button" onclick="aggiungiMultiTimerCucina()" style="background: #f59e0b; color: #05070c; border: none; padding: 6px 12px; border-radius: 6px; font-size: 11px; font-weight: 900; cursor: pointer;">+ Aggiungi</button>
                    </div>
                    <div id="lista-multi-timers"></div>
                </div>

                <!-- NUOVA RICETTA -->
                <div class="card-form">
                    <form action="/aggiungi_ricetta#tab-cucina" method="post">
                        <h3>🍳 Nuova Ricetta & Utensili</h3>
                        <label>Nome Ricetta</label><input type="text" name="titolo" placeholder="es. Carbonara Cyber" required>
                        <label>Categoria</label>
                        <select name="categoria">
                            <option value="Primo Piatto">🍝 Primo Piatto</option>
                            <option value="Secondo Piatto">🥩 Secondo Piatto</option>
                            <option value="Dolce / Dessert">🍰 Dolce / Dessert</option>
                            <option value="Altro">🥗 Altro / Snack</option>
                        </select>
                        <label>Utensili Necessari</label><input type="text" name="utensili" placeholder="es. Pentola grande, padella antiaderente, frusta" required>
                        <label>Ingredienti (separati da virgola - check per la spesa)</label>
                        <textarea name="ingredienti" rows="3" placeholder="es. Spaghetti, Guanciale, Uova, Pecorino" required></textarea>
                        <label>Procedimento</label>
                        <textarea name="procedimento" rows="4" placeholder="es. Rosolare il guanciale, cuocere la pasta..." required></textarea>
                        <button type="submit" class="btn-salva" style="background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);">Salva Ricetta</button>
                    </form>
                </div>

                <div class="section-title"><span>📖 Ricettario & Utensili</span></div>
                {lista_ricette_html}
            </div>

        </div>
    </body>
    </html>
    """
    return html_content

# --- ROTTE DI GESTIONE ---
@app.post("/aggiungi_evento")
def add_evento(titolo: str = Form(...), data_ora: str = Form(...), descrizione: str = Form(""), priorita: str = Form("Ordinario")):
    data_ora = data_ora.replace("T", " ")
    if len(data_ora) == 16: data_ora += ":00"
    aggiungi_evento(titolo, data_ora, descrizione, priorita)
    return RedirectResponse(url="/#tab-agenda", status_code=303)

@app.post("/modifica_evento/{evento_id}")
def mod_evento(evento_id: int, titolo: str = Form(...), data_ora: str = Form(...), descrizione: str = Form(""), priorita: str = Form("Ordinario")):
    data_ora = data_ora.replace("T", " ")
    if len(data_ora) == 16: data_ora += ":00"
    modifica_evento(evento_id, titolo, data_ora, descrizione, priorita)
    return RedirectResponse(url="/#tab-agenda", status_code=303)

@app.post("/elimina_evento/{evento_id}")
def del_evento(evento_id: int):
    elimina_evento(evento_id)
    return RedirectResponse(url="/#tab-agenda", status_code=303)

@app.post("/toggle_evento/{evento_id}")
def tog_evento(evento_id: int):
    toggle_completato(evento_id)
    return RedirectResponse(url="/#tab-agenda", status_code=303)

@app.post("/aggiungi_spesa")
def add_spesa(titolo_documento: str = Form(...), negozi_articoli: str = Form(...)):
    aggiungi_documento_spesa(titolo_documento, negozi_articoli)
    return RedirectResponse(url="/#tab-spesa", status_code=303)

@app.post("/modifica_spesa/{spesa_id}")
def mod_spesa(spesa_id: int, titolo_documento: str = Form(...), negozi_articoli: str = Form(...)):
    modifica_documento_spesa(spesa_id, titolo_documento, negozi_articoli)
    return RedirectResponse(url="/#tab-spesa", status_code=303)

@app.post("/elimina_spesa/{spesa_id}")
def del_spesa(spesa_id: int):
    elimina_documento_spesa(spesa_id)
    return RedirectResponse(url="/#tab-spesa", status_code=303)

@app.post("/aggiungi_misura")
def add_misura(prodotto: str = Form(...), m1_tipo: str = Form(...), m1_val: str = Form(""), m2_tipo: str = Form(...), m2_val: str = Form(""), m3_tipo: str = Form(...), m3_val: str = Form(""), note_extra: str = Form("")):
    aggiungi_misura(prodotto, m1_tipo, m1_val, m2_tipo, m2_val, m3_tipo, m3_val, note_extra)
    return RedirectResponse(url="/#tab-misure", status_code=303)

@app.post("/modifica_misura/{misura_id}")
def mod_misura(misura_id: int, prodotto: str = Form(...), m1_tipo: str = Form(...), m1_val: str = Form(""), m2_tipo: str = Form(...), m2_val: str = Form(""), m3_tipo: str = Form(...), m3_val: str = Form(""), note_extra: str = Form("")):
    modifica_misura(misura_id, prodotto, m1_tipo, m1_val, m2_tipo, m2_val, m3_tipo, m3_val, note_extra)
    return RedirectResponse(url="/#tab-misure", status_code=303)

@app.post("/elimina_misura/{misura_id}")
def del_misura(misura_id: int):
    elimina_misura(misura_id)
    return RedirectResponse(url="/#tab-misure", status_code=303)

@app.post("/aggiungi_media")
def add_media(titolo: str = Form(...), tipo: str = Form(...), genere: str = Form(...), stato: str = Form(...), voto: str = Form("")):
    aggiungi_intrattenimento(titolo, tipo, genere, stato, voto)
    return RedirectResponse(url="/#tab-media", status_code=303)

@app.post("/modifica_media/{item_id}")
def mod_media(item_id: int, titolo: str = Form(...), tipo: str = Form(...), genere: str = Form(...), stato: str = Form(...), voto: str = Form("")):
    modifica_intrattenimento(item_id, titolo, tipo, genere, stato, voto)
    return RedirectResponse(url="/#tab-media", status_code=303)

@app.post("/elimina_media/{item_id}")
def del_media(item_id: int):
    elimina_intrattenimento(item_id)
    return RedirectResponse(url="/#tab-media", status_code=303)

@app.post("/aggiungi_pomodoro")
def add_pomodoro(compito: str = Form(...), categoria: str = Form("Generale")):
    aggiungi_pomodoro_task(compito, categoria)
    return RedirectResponse(url="/#tab-focus", status_code=303)

@app.post("/toggle_pomodoro/{task_id}")
def tog_pomodoro(task_id: int):
    toggle_pomodoro_task(task_id)
    return RedirectResponse(url="/#tab-focus", status_code=303)

@app.post("/elimina_pomodoro/{task_id}")
def del_pomodoro(task_id: int):
    elimina_pomodoro_task(task_id)
    return RedirectResponse(url="/#tab-focus", status_code=303)

@app.post("/pulisci_completati_pomodoro")
def clean_pomodoro():
    elimina_completati_pomodoro()
    return RedirectResponse(url="/#tab-focus", status_code=303)

@app.post("/aggiungi_capo")
def add_capo(capo: str = Form(...), categoria: str = Form(...), colore: str = Form(...), stagione: str = Form(...), posizione: str = Form(...)):
    aggiungi_capo(capo, categoria, colore, stagione, posizione)
    return RedirectResponse(url="/#tab-armadio", status_code=303)

@app.post("/elimina_capo/{capo_id}")
def del_capo(capo_id: int):
    elimina_capo(capo_id)
    return RedirectResponse(url="/#tab-armadio", status_code=303)

# Allenamento & Record
@app.post("/aggiungi_record")
def add_record(esercizio: str = Form(...), peso_tempo: str = Form(...)):
    data_rec = datetime.now().strftime("%d/%m/%Y")
    aggiungi_record(esercizio, peso_tempo, data_rec)
    return RedirectResponse(url="/#tab-allenamento", status_code=303)

@app.post("/elimina_record/{rec_id}")
def del_rec(rec_id: int):
    elimina_record(rec_id)
    return RedirectResponse(url="/#tab-allenamento", status_code=303)

@app.post("/aggiungi_scheda")
def add_scheda(giorno: str = Form(...), dettagli_esercizi: str = Form(...)):
    aggiungi_scheda_allenamento(giorno, dettagli_esercizi)
    return RedirectResponse(url="/#tab-allenamento", status_code=303)

@app.post("/modifica_scheda/{scheda_id}")
def mod_scheda(scheda_id: int, giorno: str = Form(...), dettagli_esercizi: str = Form(...)):
    modifica_scheda_allenamento(scheda_id, giorno, dettagli_esercizi)
    return RedirectResponse(url="/#tab-allenamento", status_code=303)

@app.post("/elimina_scheda/{scheda_id}")
def del_scheda(scheda_id: int):
    elimina_scheda_allenamento(scheda_id)
    return RedirectResponse(url="/#tab-allenamento", status_code=303)

# Cucina & Ricette
@app.post("/aggiungi_ricetta")
def add_ricetta(titolo: str = Form(...), categoria: str = Form(...), utensili: str = Form(...), ingredienti: str = Form(...), procedimento: str = Form(...)):
    aggiungi_ricetta(titolo, categoria, utensili, ingredienti, procedimento)
    return RedirectResponse(url="/#tab-cucina", status_code=303)

@app.post("/modifica_ricetta/{ricetta_id}")
def mod_ricetta(ricetta_id: int, titolo: str = Form(...), categoria: str = Form(...), utensili: str = Form(...), ingredienti: str = Form(...), procedimento: str = Form(...)):
    modifica_ricetta(ricetta_id, titolo, categoria, utensili, ingredienti, procedimento)
    return RedirectResponse(url="/#tab-cucina", status_code=303)

@app.post("/elimina_ricetta/{ricetta_id}")
def del_ricetta(ricetta_id: int):
    elimina_ricetta(ricetta_id)
    return RedirectResponse(url="/#tab-cucina", status_code=303)

@app.get("/ics/{evento_id}")
def scarica_ics(evento_id: int):
    eventi = ottieni_eventi()
    evento = next((e for e in eventi if e[0] == evento_id), None)
    if not evento: return RedirectResponse(url="/#tab-agenda", status_code=303)
    try:
        dt = datetime.strptime(evento[2], "%Y-%m-%d %H:%M:%S")
        dt_start, dt_end = dt.strftime("%Y%m%dT%H%M%S"), (dt + timedelta(hours=1)).strftime("%Y%m%dT%H%M%S")
    except:
        dt_start, dt_end = "20261027T150000", "20261027T160000"
    ics_content = f"""BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Cyber Suite//IT
BEGIN:VEVENT
UID:evento-{evento_id}@agenda.local
DTSTAMP:{datetime.now().strftime("%Y%m%dT%H%M%SZ")}
DTSTART:{dt_start}
DTEND:{dt_end}
SUMMARY:{evento[1]}
DESCRIPTION:{evento[3]}
END:VEVENT
END:VCALENDAR"""
    return Response(content=ics_content, media_type="text/calendar", headers={"Content-Disposition": f"attachment; filename=impegno-{evento_id}.ics"})

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("server:app", host="0.0.0.0", port=port)
