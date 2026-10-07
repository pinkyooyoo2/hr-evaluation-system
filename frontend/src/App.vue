<template>
  <div class="app-shell">
    <main class="content">
      <div v-if="!user" class="login-wrap">
        <div class="login-layout">
          <div class="login-panel">
            <div class="login-title">인사평가 시스템</div>

            <div class="login-form-block">
              <div class="field-label">로그인</div>

              <div v-if="message" class="alert" :class="message.type === 'error' ? 'alert-danger' : 'alert-success'">
                {{ message.text }}
              </div>

              <div class="mb-3">
                <label class="form-label">사번</label>
                <input v-model="form.username" type="text" class="form-control" placeholder="ADMIN 또는 사번 입력" />
              </div>

              <div class="mb-3">
                <label class="form-label">비밀번호</label>
                <input v-model="form.password" type="password" class="form-control" placeholder="비밀번호 입력" />
              </div>

              <button class="btn btn-primary w-100" @click="login" :disabled="isSubmitting">
                {{ isSubmitting ? '로그인 중...' : '로그인' }}
              </button>
            </div>
          </div>

        </div>
      </div>

      <div v-else-if="user.role === 'admin'" class="admin-layout">
        <aside class="admin-sidebar">
          <div class="brand-wrap">
            <div class="brand-badge">HR</div>
            <div class="brand-copy">
              <div class="brand-main">인사평가</div>
              <div class="brand-sub">관리 시스템</div>
            </div>
          </div>

          <nav class="nav flex-column">
            <div class="nav-section-label">평가 관리</div>
            <button class="nav-link" :class="{ active: activeTab === 'team' }" @click="activeTab='team'">
              <span class="nav-dot"></span>팀 관리
            </button>
            <button class="nav-link" :class="{ active: activeTab === 'users' }" @click="activeTab='users'">
              <span class="nav-dot"></span>사용자 관리
            </button>
            <button class="nav-link" :class="{ active: activeTab === 'items' }" @click="activeTab='items'">
              <span class="nav-dot"></span>평가 항목 관리
            </button>
            <button class="nav-link" :class="{ active: activeTab === 'status' }" @click="activeTab='status'">
              <span class="nav-dot"></span>응답 현황
            </button>
            <button class="nav-link" :class="{ active: activeTab === 'bonus' }" @click="activeTab='bonus'">
              <span class="nav-dot"></span>팀 보너스
            </button>
            <button class="nav-link" :class="{ active: activeTab === 'results' }" @click="activeTab='results'">
              <span class="nav-dot"></span>평가 결과
            </button>
          </nav>
        </aside>

        <section class="admin-right">
          <div class="admin-topbar">
            <div class="topbar-spacer"></div>
            <div class="user-box">
              <div class="user-avatar">A</div>
              <div class="user-meta">
                <span class="user-label">ADMIN</span>
                <span class="user-role">관리자</span>
              </div>
              <button class="logout-inline" @click="logout">로그아웃</button>
            </div>
          </div>

          <div class="admin-main">
            <div v-if="activeTab === 'team'" class="admin-panel admin-reference-panel">
              <div class="reference-title-row">
                <div class="reference-crumb">인사평가</div>
                <h2 class="admin-title">팀 관리</h2>
              </div>

              <div class="reference-header-panel">
                <h3>팀 관리</h3>
                <p>팀마다 매니저 한 명을 지정합니다.</p>
              </div>

              <div class="team-management-grid">
                <div class="team-form-card">
                  <div class="team-section-title">팀 추가</div>
                  <div class="field-block">
                    <label class="field-label-compact">팀명</label>
                    <input v-model="teamForm.name" type="text" class="form-control" placeholder="팀명 입력" />
                  </div>
                  <div class="field-block">
                    <label class="field-label-compact">매니저</label>
                    <select v-model="teamForm.manager" class="form-select">
                      <option value="">매니저 선택</option>
                      <option v-for="manager in managers" :key="manager.id" :value="manager.id">{{ manager.name || manager.username }}</option>
                    </select>
                  </div>
                  <button class="btn btn-primary btn-wide" @click="createTeam">팀 추가</button>
                </div>

                <div class="team-list-card">
                  <table class="reference-team-table">
                    <thead>
                      <tr>
                        <th>팀명</th>
                        <th>매니저</th>
                        <th>관리</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-for="team in teams" :key="team.id">
                        <td>{{ team.name }}</td>
                        <td>{{ team.manager_name || team.manager }}</td>
                        <td class="cell-actions">
                          <button class="action-btn action-edit" @click="adminSelectedTeamId = String(team.id); activeTab = 'bonus'">수정</button>
                          <button class="action-btn action-delete" @click="deleteTeam(team.id)">삭제</button>
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>
            </div>

            <div v-else-if="activeTab === 'status'" class="admin-panel">
              <div class="reference-title-row">
                <h2 class="admin-title">응답 현황</h2>
              </div>
              <div class="reference-header-panel">
                <h3>응답 현황</h3>
                <p>팀별 매니저 평가 제출 현황입니다.</p>
              </div>

              <div class="status-block">
                <table class="status-table status-table-accordion">
                  <thead>
                    <tr>
                      <th>팀</th>
                      <th>매니저</th>
                      <th>평가 대상</th>
                      <th>제출</th>
                      <th>미제출</th>
                    </tr>
                  </thead>
                  <tbody>
                    <template v-for="row in statusTableRows" :key="row.team_id">
                      <tr class="status-main-row">
                        <td>{{ row.team_name }}</td>
                        <td>{{ row.manager_name }}</td>
                        <td>{{ row.target_count }}명</td>
                        <td>{{ row.submitted_count }}명</td>
                        <td>{{ row.missing_count }}명</td>
                      </tr>

                      <tr v-for="employee in row.employee_rows" :key="`${row.team_id}-${employee.username}`" class="status-sub-row">
                        <td class="status-sub-label"> </td>
                        <td class="status-employee-cell">
                          <span>{{ employee.name }} ({{ employee.username }})</span>
                        </td>
                        <td> </td>
                        <td>
                          <span :class="employee.status === '제출 완료' ? 'status-complete' : 'status-pending'">
                            {{ employee.status }}
                          </span>
                        </td>
                        <td> </td>
                      </tr>
                    </template>
                  </tbody>
                </table>
              </div>

              <div class="status-card-section">
                <h3 class="status-card-title">미제출 매니저</h3>
                <div v-if="unsubmittedManagers.length === 0" class="empty-manager-message">미제출 매니저가 없습니다.</div>
                <div v-else class="status-manager-list">
                  <div v-for="manager in unsubmittedManagers" :key="manager.name" class="status-manager-pill">
                    {{ manager.name }}
                  </div>
                </div>
              </div>
            </div>

            <div v-else-if="activeTab === 'users'" class="admin-panel">
              <div class="reference-title-row">
                <div class="reference-crumb">인사평가</div>
                <h2 class="admin-title">사용자 관리</h2>
              </div>
              <div class="reference-header-panel">
                <h3>사용자 관리</h3>
                <p>관리자, 매니저, 직원을 한 번에 관리합니다.</p>
              </div>
              <div class="status-block">
                <div class="sub-section-title">사용자 목록</div>
                <table class="status-table">
                  <thead>
                    <tr>
                      <th>사번</th>
                      <th>이름</th>
                      <th>역할</th>
                      <th>팀</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="userRow in adminUsers" :key="userRow.id">
                      <td>{{ userRow.username }}</td>
                      <td>{{ userRow.name || '-' }}</td>
                      <td>{{ roleLabel(userRow.role) }}</td>
                      <td>{{ userRow.team_name || userRow.team || '-' }}</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>

            <div v-else-if="activeTab === 'items'" class="admin-panel">
              <div class="reference-title-row">
                <h2 class="admin-title">평가 항목 관리</h2>
              </div>
              <div class="reference-header-panel">
                <h3>평가 항목 관리</h3>
                <p>전체 가중치 합계가 100이 되도록 항목을 함께 저장합니다.</p>
              </div>

              <div class="item-form-card">
                <div class="item-form-list">
                  <div v-for="(item, index) in itemEditRows" :key="item.id ?? `new-item-${index}`" class="item-edit-row">
                    <div class="item-field item-name-field">
                      <label>평가 항목</label>
                      <input v-model="item.name" type="text" class="form-control" placeholder="평가 항목 입력" />
                    </div>

                    <div class="item-field item-weight-field">
                      <label>가중치</label>
                      <div class="weight-input-wrap">
                        <input v-model.number="item.weight" type="number" min="0" max="100" class="form-control" />
                        <span class="weight-unit">점</span>
                      </div>
                    </div>

                    <button class="action-btn action-delete item-delete-btn" @click="removeItemRow(index)">삭제</button>
                  </div>
                </div>

                <div class="item-actions-bar">
                  <div class="item-actions-left">
                    <button class="btn item-add-btn" @click="addItemRow">+ 항목 추가</button>
                    <span class="weight-total">현재 가중치 합계: {{ currentItemTotal }}</span>
                  </div>
                  <button class="btn btn-primary item-save-btn" @click="saveAllItems">전체 저장</button>
                </div>
              </div>
            </div>

            <div v-else-if="activeTab === 'bonus'" class="admin-panel">
              <div class="reference-title-row">
                <div class="reference-crumb">인사평가</div>
                <h2 class="admin-title">팀 보너스</h2>
              </div>

              <div class="reference-header-panel panel-header-surface">
                <h3>팀 보너스 점수</h3>
                <p>입력한 점수로 해당 팀의 보너스를 설정합니다. 다시 저장하면 기존 점수를 교체합니다.</p>
              </div>

              <div class="bonus-grid">
                <div class="bonus-card">
                  <div class="bonus-card-header">팀 보너스 설정</div>

                  <div class="field-block">
                    <label class="field-label-compact">팀</label>
                    <select v-model="adminSelectedTeamId" class="form-select">
                      <option value="">팀 선택</option>
                      <option v-for="team in teams" :key="team.id" :value="team.id">{{ team.name }}</option>
                    </select>
                  </div>

                  <div class="field-block">
                    <label class="field-label-compact">보너스 점수</label>
                    <input v-model.number="selectedTeamBonus" type="number" min="0" max="10" class="form-control" placeholder="0" />
                  </div>

                  <button class="btn btn-primary btn-wide btn-bonus-save" @click="saveSelectedTeamBonus">팀 보너스 저장</button>
                </div>

                <div class="bonus-card">
                  <div class="bonus-card-header">현재 보너스</div>
                  <table class="bonus-table">
                    <thead>
                      <tr>
                        <th>팀</th>
                        <th>현재 보너스</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-for="team in teams" :key="team.id">
                        <td>{{ team.name }}</td>
                        <td>{{ team.bonus_score ?? 0 }}점</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>
            </div>

            <div v-else-if="activeTab === 'results'" class="admin-panel">
              <div class="results-header-row">
                <div class="results-header-copy">
                  <h2 class="admin-title">평가 결과</h2>
                  <p>개인 점수와 팀별 평가 분석을 확인합니다.</p>
                </div>
                <div class="results-substatus">제출 {{ personalRows.filter((row) => row.status === '제출').length }} / {{ Math.max(personalRows.length, 1) }}명</div>
              </div>

              <div class="results-stack">
                <div class="result-card result-card-full">
                  <div class="card-head">
                    <h4>개인 점수</h4>
                  </div>
                  <div class="results-table-wrap">
                    <table class="result-table">
                      <thead>
                        <tr>
                          <th>사번</th>
                          <th>성명</th>
                          <th>팀</th>
                          <th>개인 평가 점수</th>
                          <th>팀 보너스</th>
                          <th>최종 점수</th>
                          <th>상태</th>
                        </tr>
                      </thead>
                      <tbody>
                        <tr v-for="row in personalRows" :key="row.employee_id">
                          <td>{{ row.username }}</td>
                          <td>{{ row.name }}</td>
                          <td>{{ row.team_name }}</td>
                          <td>{{ row.personal_score }}</td>
                          <td>{{ formatBonus(row.team_bonus) }}</td>
                          <td>{{ row.final_score }}</td>
                          <td>
                            <span class="result-status-pill" :class="row.status === '제출' ? 'status-submitted' : 'status-pending'">
                              {{ row.status }}
                            </span>
                          </td>
                        </tr>
                      </tbody>
                    </table>
                  </div>
                </div>

                <div class="results-two-col">
                  <div class="result-card">
                    <div class="card-head">
                      <h4>팀별 평균 점수</h4>
                    </div>
                    <div class="mini-legend">
                      <span v-for="item in teamAverageData" :key="item.team_name" class="legend-item">
                        <i :style="{ background: getDistributionColor(item.avg_score >= 80 ? '80' : item.avg_score >= 70 ? '70' : '60') }"></i>
                        {{ item.team_name }}
                      </span>
                    </div>
                    <div class="horizontal-bar-chart">
                      <div v-for="item in teamAverageData" :key="item.team_name" class="hbar-row">
                        <div class="hbar-label">{{ item.team_name }}</div>
                        <div class="hbar-track">
                          <div class="hbar-fill" :style="{ width: `${Math.min(item.avg_score, 100)}%` }"></div>
                        </div>
                        <div class="hbar-value">{{ formatScore(item.avg_score) }}</div>
                      </div>
                    </div>
                  </div>

                  <div class="result-card">
                    <div class="card-head">
                      <h4>팀별 직원 평가 점수 분포</h4>
                    </div>
                    <div class="distribution-legend">
                      <span v-for="team in teamDistributionData" :key="team.team_name" class="legend-item">
                        <i :style="{ background: team.team_name === '개발팀' ? '#7ecb9d' : '#f3b36d' }"></i>
                        {{ team.team_name }}
                      </span>
                    </div>
                    <div class="range-chart">
                      <div v-for="(bin, index) in (teamDistributionData[0]?.bins || [])" :key="`range-${bin.label}`" class="range-column">
                        <div class="range-bars">
                          <div v-for="team in teamDistributionData" :key="`${team.team_name}-${bin.label}`" class="range-bar" :style="{ height: `${Math.max((team.bins[index]?.count || 0) * 38, 0)}px`, background: team.team_name === '개발팀' ? '#7ecb9d' : '#f3b36d' }" :title="`${team.team_name}: ${team.bins[index]?.count || 0}명`"></div>
                        </div>
                        <div class="range-label">{{ formatRangeLabel(bin.label) }}</div>
                      </div>
                    </div>
                    <div class="range-axis-label">최종 점수 구간</div>
                  </div>
                </div>

                <div class="result-card radar-card">
                  <div class="card-head">
                    <h4>평가 항목별 팀 평균 점수</h4>
                  </div>
                  <div class="radar-wrap">
                    <svg viewBox="0 0 240 240" class="radar-svg" role="img" aria-label="평가 항목별 팀 평균 점수">
                      <polygon points="120,20 200,70 180,180 120,220 60,180 40,70" fill="none" stroke="#dfe7f1" stroke-width="1" />
                      <polygon points="120,50 180,90 160,170 120,200 80,170 60,90" fill="none" stroke="#e3ebf5" stroke-width="1" />
                      <polygon points="120,80 150,110 140,150 120,170 100,150 90,110" fill="none" stroke="#e3ebf5" stroke-width="1" />
                      <g v-for="(label, index) in radarData.labels" :key="label" class="radar-axis">
                        <line :x1="120" :y1="120" :x2="120 + Math.cos((-Math.PI / 2) + (index / radarData.labels.length) * (Math.PI * 2)) * 90" :y2="120 + Math.sin((-Math.PI / 2) + (index / radarData.labels.length) * (Math.PI * 2)) * 90" stroke="#d7e3f3" stroke-width="1" />
                        <text :x="120 + Math.cos((-Math.PI / 2) + (index / radarData.labels.length) * (Math.PI * 2)) * 104" :y="120 + Math.sin((-Math.PI / 2) + (index / radarData.labels.length) * (Math.PI * 2)) * 104" text-anchor="middle" dominant-baseline="middle" font-size="8">{{ label.slice(0, 4) }}</text>
                      </g>
                      <polygon v-for="(series, index) in radarData.series" :key="series.team_name" :points="radarPoints(series.values)" :fill="getRadarColor(index)" :stroke="getRadarColor(index)" fill-opacity="0.18" stroke-width="1.5" />
                    </svg>
                  </div>
                  <div class="radar-caption">5점 만점</div>
                </div>

                <div class="download-box">
                  <div class="download-row">
                    <div>
                      <h4>평가 결과 CSV 다운로드</h4>
                      <p>CSV 파일은 Excel에서 열 수 있습니다.</p>
                    </div>
                    <a class="btn btn-primary csv-btn" :href="'/api/evaluations/results/csv/'" target="_blank">CSV 파일 다운로드 (.csv)</a>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>
      </div>

      <div v-else class="role-layout">
        <aside class="admin-sidebar role-sidebar">
          <div class="brand-wrap">
            <div class="brand-badge">HR</div>
            <div class="brand-copy">
              <div class="brand-main">인사평가</div>
              <div class="brand-sub">관리 시스템</div>
            </div>
          </div>

          <nav class="nav flex-column">
            <div class="nav-section-label">평가</div>
            <button class="nav-link active" type="button">
              <span class="nav-dot"></span>내 최종 점수
            </button>
          </nav>
        </aside>

        <section class="admin-right">
          <div class="admin-topbar employee-topbar">
            <div class="topbar-title-wrap">
              <div class="reference-crumb">인사평가</div>
              <h2 class="admin-title">내 최종 점수</h2>
            </div>
            <div class="user-box">
              <div class="user-avatar user-avatar-employee">직</div>
              <div class="user-meta">
                <span class="user-label">{{ user.name || user.username }}</span>
                <span class="user-role">{{ roleLabel(user.role) }}</span>
              </div>
              <button class="logout-inline" @click="logout">로그아웃</button>
            </div>
          </div>

          <div class="admin-main employee-main">
            <div class="employee-summary-panel">
              <div class="employee-summary-header">
                <h2>내 최종 점수</h2>
                <p>본인의 평가 결과를 확인합니다.</p>
              </div>

              <div v-if="employeeScore" class="score-card-row employee-score-card-row">
                <div class="score-card employee-score-card">
                  <div class="label">개인 평가 점수</div>
                  <div class="value">{{ employeeScore.personal_score }}</div>
                </div>
                <div class="score-card employee-score-card">
                  <div class="label">팀 보너스</div>
                  <div class="value">{{ formatBonus(employeeScore.team_bonus) }}</div>
                </div>
                <div class="score-card employee-score-card accent">
                  <div class="label">최종 점수</div>
                  <div class="value">{{ employeeScore.final_score }}</div>
                </div>
              </div>
              <p v-else class="empty-score-message">아직 제출된 평가 결과가 없습니다.</p>
            </div>
          </div>
        </section>
      </div>
    </main>
  </div>
</template>

<script setup>
import { computed, ref, onMounted, watch } from 'vue';

const form = ref({ username: 'ADMIN', password: 'admin1234!' });
const message = ref(null);
const user = ref(null);
const isSubmitting = ref(false);
const activeTab = ref('dashboard');

const teams = ref([]);
const managers = ref([]);
const adminUsers = ref([]);
const evaluationItems = ref([]);
const statusRows = ref([]);
const teamMembers = ref([]);
const employeeScore = ref(null);
const selectedEmployeeId = ref('');
const evaluationScores = ref({});
const adminSelectedTeamId = ref('');
const selectedTeamBonus = ref(0);
const resultSummary = ref({ personal_rows: [], team_average: [], team_distribution: [], radar: { labels: [], series: [] } });
const itemEditRows = ref([]);

const teamForm = ref({ name: '', manager: '', bonus_score: 0 });
const userForm = ref({ username: '', name: '', role: 'employee', team: '', password: '' });
const itemForm = ref({ name: '', weight: 0, description: '' });

const currentAdminTeamName = computed(() => {
  const team = teams.value.find((item) => String(item.id) === String(adminSelectedTeamId.value));
  return team ? team.name : '팀 선택';
});

const pageTitle = computed(() => {
  if (!user.value) return '로그인';
  if (user.value.role === 'admin') return '인사평가 시스템';
  if (user.value.role === 'manager') return '매니저 평가 입력';
  return '직원 평가 결과';
});

const personalRows = computed(() => resultSummary.value.personal_rows || []);
const teamAverageData = computed(() => resultSummary.value.team_average || []);
const teamDistributionData = computed(() => resultSummary.value.team_distribution || []);
const radarData = computed(() => resultSummary.value.radar || { labels: [], series: [] });
const currentItemTotal = computed(() => itemEditRows.value.reduce((sum, row) => sum + (Number(row.weight) || 0), 0));
const statusTableRows = computed(() =>
  statusRows.value.map((row) => {
    const teamEmployees = adminUsers.value.filter(
      (user) => user.role === 'employee' && Number(user.team) === Number(row.team_id)
    );
    const submittedEmployeeIds = new Set((row.submitted_employee_ids || []).map((id) => Number(id)));
    const employees = teamEmployees.map((user) => ({
      id: user.id,
      name: user.name || user.username,
      username: user.username,
      status: submittedEmployeeIds.has(Number(user.id)) ? '제출 완료' : '미제출',
    }));

    return {
      ...row,
      target_count: Number(row.total_members || 0),
      missing_count: Math.max(Number(row.total_members || 0) - Number(row.submitted_count || 0), 0),
      employee_rows: employees,
    };
  })
);

const unsubmittedManagers = computed(() =>
  statusRows.value
    .filter((row) => Number(row.total_members || 0) > Number(row.submitted_count || 0))
    .map((row) => ({
      name: row.manager_name || '미지정',
    }))
);

function formatScore(value) {
  if (typeof value === 'number') {
    return Number(value).toFixed(1);
  }
  return value;
}

function formatRangeLabel(label) {
  const normalized = String(label || '').trim();
  if (normalized === '60') return '60 미만';
  if (normalized === '70') return '60-69';
  if (normalized === '80') return '70-79';
  if (normalized === '90') return '80-89';
  return normalized;
}

function formatBonus(value) {
  const numeric = Number(value) || 0;
  return numeric >= 0 ? `+${numeric}` : `${numeric}`;
}

function radarPoints(values) {
  if (!values || !values.length) return '';
  const centerX = 120;
  const centerY = 120;
  const radius = 90;

  return values.map((value, index) => {
    const angle = (-Math.PI / 2) + (index / values.length) * (Math.PI * 2);
    const distance = (Number(value) / 100) * radius;
    const x = centerX + Math.cos(angle) * distance;
    const y = centerY + Math.sin(angle) * distance;
    return `${x},${y}`;
  }).join(' ');
}

function getDistributionColor(label) {
  const palette = ['#60a5fa', '#34d399', '#fbbf24', '#f59e0b'];
  const index = ['60', '70', '80', '90'].indexOf(String(label));
  return palette[index >= 0 ? index : 0];
}

function getRadarColor(index) {
  const palette = ['#60a5fa', '#34d399', '#fbbf24', '#f97316'];
  return palette[index % palette.length];
}

function roleLabel(role) {
  if (role === 'admin') return '관리자';
  if (role === 'manager') return '매니저';
  return '직원';
}

function getCsrfToken() {
  const value = document.cookie
    .split('; ')
    .find((row) => row.startsWith('csrftoken='));
  return value ? value.split('=')[1] : '';
}

async function fetchJson(url, options = {}) {
  const baseUrl = (import.meta.env.VITE_API_BASE_URL || '').replace(/\/$/, '');
  const targetUrl = /^https?:\/\//i.test(url) ? url : `${baseUrl}${url}`;

  const response = await fetch(targetUrl, {
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': getCsrfToken(),
      ...(options.headers || {}),
    },
    ...options,
  });

  const text = await response.text();
  const data = text ? JSON.parse(text) : {};

  if (!response.ok) {
    throw new Error(data.error || data.detail || '요청에 실패했습니다.');
  }

  return data;
}

async function login() {
  isSubmitting.value = true;
  message.value = null;

  try {
    const data = await fetchJson('/api/login/', {
      method: 'POST',
      body: JSON.stringify(form.value),
    });

    user.value = data.user;
    message.value = { type: 'success', text: data.message || '로그인 성공' };
    activeTab.value = user.value.role === 'admin' ? 'team' : 'dashboard';
    await loadRoleData();
  } catch (error) {
    message.value = { type: 'error', text: error.message };
  } finally {
    isSubmitting.value = false;
  }
}

async function logout() {
  try {
    await fetchJson('/api/logout/', { method: 'POST' });
  } catch (error) {
    console.warn(error);
  } finally {
    user.value = null;
    activeTab.value = 'dashboard';
    message.value = { type: 'success', text: '로그아웃 되었습니다.' };
  }
}

async function loadRoleData() {
  if (!user.value) return;

  if (user.value.role === 'admin') {
    await loadAdminData();
  }

  if (user.value.role === 'manager') {
    await loadManagerData();
  }

  if (user.value.role === 'employee') {
    await loadEmployeeScore();
  }
}

async function loadAdminData() {
  const [teamData, userData, itemData, statusData, resultData] = await Promise.all([
    fetchJson('/api/teams/'),
    fetchJson('/api/users/'),
    fetchJson('/api/evaluation-items/'),
    fetchJson('/api/evaluations/status/'),
    fetchJson('/api/evaluations/results/summary/'),
  ]);

  teams.value = teamData;
  managers.value = userData.filter((item) => item.role === 'manager');
  adminUsers.value = userData;
  evaluationItems.value = itemData;
  itemEditRows.value = itemData.map((item) => ({
    id: item.id,
    name: item.name,
    weight: Number(item.weight) || 0,
    description: item.description || '',
  }));
  statusRows.value = statusData;
  resultSummary.value = resultData;

  if (!adminSelectedTeamId.value && teamData.length) {
    adminSelectedTeamId.value = String(teamData[0].id);
  }

  if (adminSelectedTeamId.value) {
    const selectedTeam = teamData.find((team) => String(team.id) === String(adminSelectedTeamId.value));
    selectedTeamBonus.value = selectedTeam ? Number(selectedTeam.bonus_score || 0) : 0;
  }
}

async function loadManagerData() {
  const teamData = await fetchJson('/api/teams/');
  const userData = await fetchJson('/api/users/');

  const myTeam = teamData.find((team) => team.manager === user.value.id) || teamData.find((team) => Number(team.manager) === Number(user.value.id));
  const teamId = myTeam ? myTeam.id : null;
  teamMembers.value = userData.filter((item) => item.role === 'employee' && Number(item.team) === Number(teamId));

  if (teamId && !selectedEmployeeId.value) {
    selectedEmployeeId.value = teamMembers.value[0]?.id || '';
  }

  evaluationItems.value = await fetchJson('/api/evaluation-items/');
  if (selectedEmployeeId.value && evaluationItems.value.length) {
    const current = await fetchJson('/api/evaluations/responses/');
    const target = current.find((item) => Number(item.employee) === Number(selectedEmployeeId.value));
    const scoreData = target?.score_values || {};
    evaluationScores.value = {};
    evaluationItems.value.forEach((item) => {
      evaluationScores.value[item.id] = scoreData[item.id] ?? scoreData[String(item.id)] ?? 1;
    });
  }
}

async function loadEmployeeScore() {
  employeeScore.value = await fetchJson('/api/evaluations/my-score/');
}

async function createTeam() {
  await fetchJson('/api/teams/', {
    method: 'POST',
    body: JSON.stringify(teamForm.value),
  });
  teamForm.value = { name: '', manager: '', bonus_score: 0 };
  await loadAdminData();
}

async function saveTeamBonus(team) {
  await fetchJson(`/api/teams/${team.id}/`, {
    method: 'PATCH',
    body: JSON.stringify({ bonus_score: team.bonus_score }),
  });
  await loadAdminData();
}

async function saveSelectedTeamBonus() {
  if (!adminSelectedTeamId.value) return;
  await fetchJson(`/api/teams/${adminSelectedTeamId.value}/`, {
    method: 'PATCH',
    body: JSON.stringify({ bonus_score: Number(selectedTeamBonus.value) }),
  });
  await loadAdminData();
}

async function deleteTeam(teamId) {
  await fetchJson(`/api/teams/${teamId}/`, { method: 'DELETE' });
  await loadAdminData();
}

async function createUser() {
  await fetchJson('/api/users/', {
    method: 'POST',
    body: JSON.stringify(userForm.value),
  });
  userForm.value = { username: '', name: '', role: 'employee', team: '', password: '' };
  await loadAdminData();
}

function addItemRow() {
  itemEditRows.value.push({
    id: null,
    name: '',
    weight: 0,
    description: '',
  });
}

async function removeItemRow(index) {
  const row = itemEditRows.value[index];
  if (!row) return;

  if (row.id) {
    await fetchJson(`/api/evaluation-items/${row.id}/`, { method: 'DELETE' });
  }

  itemEditRows.value.splice(index, 1);
  await loadAdminData();
}

async function saveAllItems() {
  const rows = itemEditRows.value.map((row) => ({
    id: row.id,
    name: String(row.name || '').trim(),
    weight: Number(row.weight) || 0,
    description: row.description || '',
  }));

  if (rows.some((row) => !row.name)) {
    message.value = { type: 'error', text: '평가 항목명을 입력해 주세요.' };
    return;
  }

  if (rows.reduce((sum, row) => sum + row.weight, 0) !== 100) {
    message.value = { type: 'error', text: '가중치 합계는 100이어야 합니다.' };
    return;
  }

  try {
    for (const row of rows) {
      if (row.id) {
        await fetchJson(`/api/evaluation-items/${row.id}/`, {
          method: 'PATCH',
          body: JSON.stringify({
            name: row.name,
            weight: row.weight,
            description: row.description,
          }),
        });
      } else {
        await fetchJson('/api/evaluation-items/', {
          method: 'POST',
          body: JSON.stringify({
            name: row.name,
            weight: row.weight,
            description: row.description,
          }),
        });
      }
    }

    message.value = { type: 'success', text: '평가 항목이 저장되었습니다.' };
    await loadAdminData();
  } catch (error) {
    message.value = { type: 'error', text: error.message };
  }
}

async function createItem() {
  await fetchJson('/api/evaluation-items/', {
    method: 'POST',
    body: JSON.stringify(itemForm.value),
  });
  itemForm.value = { name: '', weight: 0, description: '' };
  await loadAdminData();
}

async function saveEvaluation(submit) {
  if (!selectedEmployeeId.value) return;
  const payload = {
    employee: Number(selectedEmployeeId.value),
    score_values: {},
    temporary_save: evaluationScores.value,
    is_submitted: submit,
  };

  Object.entries(evaluationScores.value).forEach(([key, value]) => {
    payload.score_values[key] = Number(value);
  });

  await fetchJson('/api/evaluations/responses/', {
    method: 'POST',
    body: JSON.stringify(payload),
  });

  if (submit) {
    message.value = { type: 'success', text: '평가가 제출되었습니다.' };
  } else {
    message.value = { type: 'success', text: '임시 저장되었습니다.' };
  }
  await loadManagerData();
}

watch(
  () => adminSelectedTeamId.value,
  (nextId) => {
    if (!nextId) return;
    const team = teams.value.find((item) => String(item.id) === String(nextId));
    if (team) {
      selectedTeamBonus.value = Number(team.bonus_score || 0);
    }
  },
  { immediate: true }
);

onMounted(async () => {
  try {
    const me = await fetchJson('/api/me/');
    user.value = me.user;
    if (user.value?.role === 'admin') {
      activeTab.value = 'team';
    }
    await loadRoleData();
  } catch (error) {
    user.value = null;
  }
});
</script>
