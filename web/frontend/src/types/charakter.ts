export interface WuerfelState {
  value: number
  modifier: number
  typ: string
}

export interface FertigkeitState {
  fertigkeit_name: string
  grundfertigkeit: boolean
  ausgewaehlt: boolean
  aktiv: boolean
  wuerfel: WuerfelState
  attribut: string | null
  custom?: boolean
}

export interface AttributState {
  attribut_name: string
  wert: number
  modifier: number
}

export interface CharakterDaten {
  profil_daten: Record<string, string>
  active_setting_name: string
  char_gen_completed: boolean
  attribute: Record<string, AttributState>
  fertigkeiten: Record<string, FertigkeitState>
  selected_handicaps: string[]
  selected_talente: string[]
  selected_maechte: string[]
  voelker_selected: Record<string, any>
  verbleibende_attributsteigerungen?: number
  verbleibende_fertigkeitssteigerungen?: number
  maximale_attributsteigerungen?: number
  maximale_fertigkeitssteigerungen?: number
  gesamt_handicap_punkte?: number
  verbleibende_handicap_punkte?: number
  settingregeln?: Record<string, boolean>
}

export interface CharakterListItem {
  id: number
  char_name: string
  active_setting_name: string
  char_gen_completed: boolean
  aktualisiert_am: string
}

export interface CharakterDetail extends CharakterListItem {
  charakter_daten: CharakterDaten
  erstellt_am: string
}
