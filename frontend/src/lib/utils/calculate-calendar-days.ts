/**
 * 달력 그리드용 날짜 배열 생성.
 *
 * 월요일 시작 달력을 위해:
 * 1. 해당 월의 1일이 무슨 요일인지 확인
 * 2. 월요일부터 시작하도록 이전 달 날짜로 그리드 채움
 * 3. 다음 월 첫 번째 월요일 전까지 날짜 생성
 */
import type { CalendarDay } from '$lib';

export function calculateCalendarDays(year: number, month: number): CalendarDay[] {
    const monthIndex = month - 1;  // Date 객체는 0-based month 사용
    const days: CalendarDay[] = [];

    const firstDateOfMonth = new Date(year, monthIndex, 1);
    const lastDateOfMonth = new Date(year, monthIndex + 1, 0);  // 다음달 0일 = 이번달 마지막일

    // 월요일 시작을 위한 오프셋 계산
    // getDay(): 일=0, 월=1, ..., 토=6
    // 월요일 시작이므로: 일요일(0)은 6일 전, 월요일(1)은 0일 전, ...
    const startDayOfWeek = firstDateOfMonth.getDay();
    const offset = startDayOfWeek === 0 ? 6 : startDayOfWeek - 1;
    const gridStartDate = new Date(year, monthIndex, 1 - offset);

    let currentDate = new Date(gridStartDate);

    // 그리드가 월요일에 끝나고 해당 월을 벗어날 때까지 반복
    while (true) {
        days.push({
            date: new Date(currentDate),
            isCurrentMonth: currentDate.getMonth() === monthIndex
        });

        currentDate.setDate(currentDate.getDate() + 1);

        // 다음 주 월요일이고 이번 달을 넘어갔으면 종료
        if (currentDate.getDay() === 1 && currentDate > lastDateOfMonth) {
            break;
        }
    }

    return days;
}