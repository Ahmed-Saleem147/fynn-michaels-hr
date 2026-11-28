-- Fynn-Micheals HR Solutions: job listings and applications.
--
-- Run this once in the Supabase dashboard (SQL Editor > New query > paste > Run).
-- It is safe to run again: everything uses "if not exists" / "or replace".
--
-- Who can do what:
--   * Visitors (anon)  - see open jobs; submit an application; upload a CV.
--                        They can never read applications or CVs back.
--   * Admins           - signed-in users listed in public.admins: full control.
--
-- After running it, add the owner as an admin (see README, "Careers and the admin page").

-- ------------------------------------------------------------------ admins
create table if not exists public.admins (
  user_id uuid primary key references auth.users (id) on delete cascade,
  created_at timestamptz not null default now()
);
alter table public.admins enable row level security;

create or replace function public.is_admin()
returns boolean
language sql
stable
security definer
set search_path = public
as $$
  select exists (select 1 from public.admins where user_id = auth.uid());
$$;

drop policy if exists "admins read own row" on public.admins;
create policy "admins read own row" on public.admins
  for select to authenticated using (user_id = auth.uid());

-- ------------------------------------------------------------------ jobs
create table if not exists public.jobs (
  id uuid primary key default gen_random_uuid(),
  title text not null check (length(trim(title)) > 0),
  company text,                       -- client's name, or blank for a confidential client
  location text,
  employment_type text,               -- Full-time, Part-time, Contract, Internship ...
  salary text,
  summary text,                       -- one or two lines shown on the listing
  description text,                   -- full details; blank lines start new paragraphs, "- " starts a bullet
  closing_date date,
  status text not null default 'open' check (status in ('draft', 'open', 'closed')),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);
alter table public.jobs enable row level security;

create or replace function public.touch_updated_at()
returns trigger language plpgsql as $$
begin
  new.updated_at = now();
  return new;
end;
$$;

drop trigger if exists jobs_touch on public.jobs;
create trigger jobs_touch before update on public.jobs
  for each row execute function public.touch_updated_at();

-- A job is visible to the public while it is open and its closing date has not passed.
create or replace function public.job_is_live(j public.jobs)
returns boolean language sql stable as $$
  select j.status = 'open' and (j.closing_date is null or j.closing_date >= current_date);
$$;

drop policy if exists "public reads live jobs" on public.jobs;
create policy "public reads live jobs" on public.jobs
  for select to anon, authenticated using (public.job_is_live(jobs));

drop policy if exists "admins manage jobs" on public.jobs;
create policy "admins manage jobs" on public.jobs
  for all to authenticated using (public.is_admin()) with check (public.is_admin());

-- ------------------------------------------------------------------ applications
create table if not exists public.applications (
  id uuid primary key default gen_random_uuid(),
  job_id uuid not null references public.jobs (id) on delete cascade,
  full_name text not null check (length(trim(full_name)) between 1 and 200),
  email text not null check (email ~* '^[^@\s]+@[^@\s]+\.[^@\s]+$'),
  phone text check (phone is null or length(phone) <= 40),
  location text check (location is null or length(location) <= 200),
  linkedin text check (linkedin is null or length(linkedin) <= 300),
  cover_note text check (cover_note is null or length(cover_note) <= 5000),
  cv_path text check (cv_path is null or cv_path ~ '^[0-9a-f-]{36}/[A-Za-z0-9._-]{1,120}$'),
  status text not null default 'new'
    check (status in ('new', 'reviewing', 'shortlisted', 'interview', 'rejected', 'hired')),
  notes text,                         -- the owner's private notes
  created_at timestamptz not null default now()
);
alter table public.applications enable row level security;
create index if not exists applications_job_idx on public.applications (job_id, created_at desc);

-- Visitors may only add an application to a live job, and only with status 'new' and no notes.
drop policy if exists "public applies to live jobs" on public.applications;
create policy "public applies to live jobs" on public.applications
  for insert to anon, authenticated
  with check (
    status = 'new' and notes is null
    and exists (select 1 from public.jobs j where j.id = job_id and public.job_is_live(j))
  );

drop policy if exists "admins manage applications" on public.applications;
create policy "admins manage applications" on public.applications
  for all to authenticated using (public.is_admin()) with check (public.is_admin());

-- ------------------------------------------------------------------ CV storage
-- Private bucket: 5 MB limit, PDF and Word files only.
insert into storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
values ('cvs', 'cvs', false, 5242880, array[
  'application/pdf',
  'application/msword',
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
])
on conflict (id) do update
  set public = false,
      file_size_limit = excluded.file_size_limit,
      allowed_mime_types = excluded.allowed_mime_types;

drop policy if exists "public uploads cvs" on storage.objects;
create policy "public uploads cvs" on storage.objects
  for insert to anon, authenticated
  with check (bucket_id = 'cvs');

drop policy if exists "admins read cvs" on storage.objects;
create policy "admins read cvs" on storage.objects
  for select to authenticated using (bucket_id = 'cvs' and public.is_admin());

drop policy if exists "admins delete cvs" on storage.objects;
create policy "admins delete cvs" on storage.objects
  for delete to authenticated using (bucket_id = 'cvs' and public.is_admin());
