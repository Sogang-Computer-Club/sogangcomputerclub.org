/**
 * 달력 이벤트 레이아웃 계산.
 *
 * 여러 날에 걸친 이벤트를 달력 그리드에 배치하기 위한 알고리즘:
 * 1. 이벤트가 주(week)를 넘어가면 각 주별로 분할
 * 2. 같은 날짜에 겹치는 이벤트는 서로 다른 "레인"에 배치 (수직으로 쌓기)
 * 3. 빈 레인을 찾아서 이벤트가 겹치지 않도록 배치
 */
import {
  differenceInDays,
  startOfWeek,
  startOfDay,
  endOfWeek,
  max,
  min,
  addDays,
} from "date-fns";
import type { Event, ProcessedEvent, CalendarDay } from "$lib";

export function calculateProcessedEvents(
  year: number,
  month: number,
  calendarDays: CalendarDay[],
  events: Event[],
): ProcessedEvent[] {
  const processedEvents: ProcessedEvent[] = [];
  // weekLanes[row][col][lane]: 각 셀의 각 레인 점유 여부
  // row: 주 (0~5), col: 요일 (0~6), lane: 수직 레이어 (0, 1, 2, ...)
  const weekLanes: boolean[][][] = Array(6)
    .fill(0)
    .map(() => []);
  const gridStartDate = calendarDays[0].date;
  const gridEndDate = calendarDays[calendarDays.length - 1].date;

  for (const event of events) {
    const startDate = event.start;
    const endDate = event.end;

    // 달력 범위를 완전히 벗어난 이벤트 건너뛰기
    if (endDate < gridStartDate || startDate > gridEndDate) {
      continue;
    }

    let pointer = new Date(startDate);

    // 이벤트가 여러 주에 걸칠 경우 주 단위로 분할 처리
    while (pointer <= endDate) {
      const weekStart = startOfWeek(pointer, { weekStartsOn: 1 }); // 월요일 시작
      const weekEnd = addDays(
        startOfDay(endOfWeek(pointer, { weekStartsOn: 1 })),
        1,
      );

      // 이번 주에 표시할 이벤트 구간 계산
      const partStartDate = max([startDate, weekStart]);
      const partEndDate = min([endDate, weekEnd]);

      // 그리드 내 위치 계산
      const startOffset = differenceInDays(partStartDate, gridStartDate);
      const duration = differenceInDays(partEndDate, partStartDate);

      if (startOffset < 0 || startOffset >= calendarDays.length) {
        pointer = addDays(weekStart, 7);
        continue;
      }

      const row = Math.floor(startOffset / 7); // 몇 번째 주
      const col = startOffset % 7; // 무슨 요일

      // 겹치지 않는 빈 레인 찾기 (greedy 알고리즘)
      let lane = 0;
      while (true) {
        let isOccupied = false;
        for (let i = 0; i < duration; i++) {
          if (weekLanes[row]?.[col + i]?.[lane]) {
            isOccupied = true;
            break;
          }
        }
        if (!isOccupied) break;
        lane++;
      }

      // 찾은 레인에 이벤트 점유 표시
      for (let i = 0; i < duration; i++) {
        if (!weekLanes[row]) weekLanes[row] = [];
        if (!weekLanes[row][col + i]) weekLanes[row][col + i] = [];
        weekLanes[row][col + i][lane] = true;
      }

      processedEvents.push({
        ...event,
        row: row + 1, // CSS grid는 1-based
        col: col + 1,
        span: duration, // 이벤트가 차지하는 칸 수
        lane, // 수직 위치 (겹치는 이벤트 구분)
      });

      pointer = addDays(weekStart, 7); // 다음 주로 이동
    }
  }

  return processedEvents;
}
