# План тестирования экспертной системы

**Версия:** 6.0
**Дата:** 16 мая 2026

---

## 1. Цели тестирования

1. **Валидация базы знаний** — убедиться, что все правила корректно срабатывают на соответствующих конфигурациях.
2. **Проверка точности расчёта** — подтвердить корректность формулы индекса защищённости.
3. **Подтверждение KPI** — точность распознавания угроз ≥ 95%.
4. **Валидация вердиктов** — убедиться, что пороги вердиктов соответствуют ожиданиям.

---

## 2. Эталонные стенды

### 2.1. Perfect Config (Идеальная конфигурация)

Все параметры безопасности настроены корректно:

| Параметр | Значение |
|----------|----------|
| clipboard_isolation | TRUE |
| disk_redirection | FALSE |
| screen_capture_protection | TRUE |
| isolation_level | STRONG |
| session_type | Container |
| mfa_enabled | TRUE |
| password_policy | STRONG |
| auth_logging | TRUE |
| cap_drop_all | TRUE |
| read_only_rootfs | TRUE |
| no_new_privileges | TRUE |
| auto_remove | TRUE |
| tmpfs_enabled | TRUE |
| vlan_segmented | TRUE |
| firewall_enabled | TRUE |
| traffic_encrypted | TRUE |
| audit_logging | TRUE |
| anomaly_detection | TRUE |

**Ожидаемый результат:** Индекс = 100, вердикт = «Безопасно», сработавших правил = 0.

### 2.2. Default Config (Конфигурация по умолчанию)

Стандартные настройки без дополнительной защиты:

| Параметр | Значение |
|----------|----------|
| clipboard_isolation | FALSE |
| disk_redirection | FALSE |
| screen_capture_protection | FALSE |
| isolation_level | MODERATE |
| session_type | Container |
| mfa_enabled | TRUE |
| password_policy | MODERATE |
| auth_logging | TRUE |
| cap_drop_all | TRUE |
| read_only_rootfs | FALSE |
| no_new_privileges | TRUE |
| auto_remove | FALSE |
| tmpfs_enabled | TRUE |
| vlan_segmented | TRUE |
| firewall_enabled | TRUE |
| traffic_encrypted | TRUE |
| audit_logging | TRUE |
| anomaly_detection | FALSE |

**Ожидаемый результат:** Индекс ≈ 88–91, вердикт = «Безопасно».

**Ожидаемые сработавшие правила:** S03, A02, C02, C04, M02.

> **Примечание:** Вердикт «Безопасно» для Default Config обусловлен тем, что сработавшие правила имеют уровни MEDIUM и LOW, что даёт небольшой штраф. Если требуется, чтобы Default Config давал вердикт «Требуется доработка», необходимо скорректировать веса правил или пороги вердиктов на этапе итеративной валидации (см. риск R4 в реестре рисков).

### 2.3. Broken Config (Намеренно уязвимая)

Критические уязвимости по всем категориям:

| Параметр | Значение |
|----------|----------|
| clipboard_isolation | FALSE |
| disk_redirection | TRUE |
| screen_capture_protection | FALSE |
| isolation_level | NONE |
| session_type | VDI |
| mfa_enabled | FALSE |
| password_policy | WEAK |
| auth_logging | FALSE |
| cap_drop_all | FALSE |
| read_only_rootfs | FALSE |
| no_new_privileges | FALSE |
| auto_remove | FALSE |
| tmpfs_enabled | FALSE |
| vlan_segmented | FALSE |
| firewall_enabled | FALSE |
| traffic_encrypted | FALSE |
| audit_logging | FALSE |
| anomaly_detection | FALSE |

**Ожидаемый результат:** Индекс ≈ 25–30, вердикт = «Уязвимо».

**Ожидаемые сработавшие правила:** S01, S02, S03, A01, A02, A03, C01, C02, C03, C04, N01, N02, N03, N04, M01, M02.

---

## 3. Метрики качества

### 3.1. Определения

| Метрика | Определение |
|---------|-------------|
| TP (True Positive) | Правило сработало, уязвимость реально существует |
| TN (True Negative) | Правило не сработало, уязвимости нет |
| FP (False Positive) | Правило сработало, уязвимости нет (ложное срабатывание) |
| FN (False Negative) | Правило не сработало, уязвимость существует (пропуск) |

### 3.2. Формулы

```
Precision = TP / (TP + FP)
Recall    = TP / (TP + FN)
F1        = 2 × Precision × Recall / (Precision + Recall)
Accuracy  = (TP + TN) / (TP + TN + FP + FN)
```

### 3.3. Целевые значения

| Метрика | Целевое значение |
|---------|------------------|
| Precision | ≥ 95% |
| Recall | ≥ 95% |
| F1 | ≥ 95% |
| Accuracy | ≥ 95% |

---

## 4. Тест-кейсы

| ID | Стенд | Ожидаемый индекс | Ожидаемый вердикт | Ожидаемые правила |
|----|-------|------------------|-------------------|-------------------|
| TC-01 | Perfect | 100 | Безопасно | ∅ |
| TC-02 | Default | 88–91 | Безопасно | S03, A02, C02, C04, M02 |
| TC-03 | Broken | 25–30 | Уязвимо | S01,S02,S03,A01,A02,A03,C01,C02,C03,C04,N01,N02,N03,N04,M01,M02 |
| TC-04 | Только clipboard | 90–91 | Безопасно | S01 |
| TC-05 | Только MFA | 93–94 | Безопасно | A01 |
| TC-06 | Только сеть | 76–77 | Требуется доработка | N01, N02, N03, N04 |

---

## 5. Процедура тестирования

### 5.1. Подготовка
1. Подготовить конфигурационный файл для каждого стенда
2. Заполнить таблицу ожидаемых результатов

### 5.2. Выполнение
1. Для каждого тест-кейса:
   - Запустить экспертную систему с конфигурацией стенда
   - Зафиксировать фактический индекс, вердикт, сработавшие правила
   - Сравнить с ожидаемыми значениями
   - Отметить Pass/Fail

### 5.3. Анализ
1. Рассчитать TP, TN, FP, FN по всем правилам и стендам
2. Рассчитать Precision, Recall, F1, Accuracy
3. Сравнить с целевыми значениями
4. При расхождениях — скорректировать веса/пороги

### 5.4. Документирование
1. Протокол тестирования с результатами по каждому тест-кейсу
2. Таблица метрик качества
3. Заключение о соответствии KPI
