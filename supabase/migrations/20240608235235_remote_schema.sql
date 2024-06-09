
SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

CREATE EXTENSION IF NOT EXISTS "pgsodium" WITH SCHEMA "pgsodium";

COMMENT ON SCHEMA "public" IS 'standard public schema';

CREATE EXTENSION IF NOT EXISTS "pg_graphql" WITH SCHEMA "graphql";

CREATE EXTENSION IF NOT EXISTS "pg_stat_statements" WITH SCHEMA "extensions";

CREATE EXTENSION IF NOT EXISTS "pgcrypto" WITH SCHEMA "extensions";

CREATE EXTENSION IF NOT EXISTS "pgjwt" WITH SCHEMA "extensions";

CREATE EXTENSION IF NOT EXISTS "supabase_vault" WITH SCHEMA "vault";

CREATE EXTENSION IF NOT EXISTS "uuid-ossp" WITH SCHEMA "extensions";

CREATE EXTENSION IF NOT EXISTS "vector" WITH SCHEMA "public";

CREATE OR REPLACE FUNCTION "public"."handle_new_user"() RETURNS "trigger"
    LANGUAGE "plpgsql" SECURITY DEFINER
    AS $$
begin
  insert into public.profiles (id, full_name, avatar_url)
  values (new.id, new.raw_user_meta_data->>'full_name', new.raw_user_meta_data->>'avatar_url');
  return new;
end;
$$;

ALTER FUNCTION "public"."handle_new_user"() OWNER TO "postgres";

CREATE OR REPLACE FUNCTION "public"."increment_column"("table_name" "text", "column_name" "text", "amount" bigint) RETURNS SETOF "record"
    LANGUAGE "plpgsql"
    AS $$
BEGIN
    RETURN QUERY EXECUTE format('UPDATE %I SET %I = %I + %s RETURNING *', table_name, column_name, column_name, increment_amount);
END;
$$;

ALTER FUNCTION "public"."increment_column"("table_name" "text", "column_name" "text", "amount" bigint) OWNER TO "postgres";

SET default_tablespace = '';

SET default_table_access_method = "heap";

CREATE TABLE IF NOT EXISTS "public"."course_chat_misconceptions" (
    "id" bigint NOT NULL,
    "created_at" timestamp with time zone DEFAULT "now"() NOT NULL,
    "name" "text" NOT NULL,
    "count" bigint DEFAULT '1'::bigint NOT NULL,
    "course_id" bigint NOT NULL
);

ALTER TABLE "public"."course_chat_misconceptions" OWNER TO "postgres";

CREATE OR REPLACE FUNCTION "public"."increment_course_chat_misconceptions"("course_id" bigint, "misconception_ids" bigint[]) RETURNS SETOF "public"."course_chat_misconceptions"
    LANGUAGE "plpgsql"
    AS $$
DECLARE
    misconception_id BIGINT;
BEGIN
    FOREACH misconception_id IN ARRAY misconception_ids
    LOOP
        RETURN QUERY EXECUTE format(
            'UPDATE course_chat_misconceptions SET count = count + 1 WHERE course_id = %L AND id = %L RETURNING *',
            course_id, misconception_id
        );
    END LOOP;
END;
$$;

ALTER FUNCTION "public"."increment_course_chat_misconceptions"("course_id" bigint, "misconception_ids" bigint[]) OWNER TO "postgres";

CREATE OR REPLACE FUNCTION "public"."increment_course_chat_topic"("course_id" bigint, "topic_id" bigint) RETURNS SETOF "record"
    LANGUAGE "plpgsql"
    AS $$
BEGIN
    RETURN QUERY EXECUTE format('UPDATE course_chat_topics SET count = count + 1 WHERE course_id = %s AND topic_id = %s RETURNING *', course_id, topic_id);
END;
$$;

ALTER FUNCTION "public"."increment_course_chat_topic"("course_id" bigint, "topic_id" bigint) OWNER TO "postgres";

CREATE TABLE IF NOT EXISTS "public"."course_chat_topics" (
    "id" bigint NOT NULL,
    "created_at" timestamp with time zone DEFAULT "now"() NOT NULL,
    "course_id" bigint NOT NULL,
    "name" "text" NOT NULL,
    "count" bigint DEFAULT '1'::bigint NOT NULL
);

ALTER TABLE "public"."course_chat_topics" OWNER TO "postgres";

CREATE OR REPLACE FUNCTION "public"."increment_course_chat_topics"("course_id" bigint, "topic_ids" bigint[]) RETURNS SETOF "public"."course_chat_topics"
    LANGUAGE "plpgsql"
    AS $$
DECLARE
    topic_id BIGINT;
BEGIN
    FOREACH topic_id IN ARRAY topic_ids
    LOOP
        RETURN QUERY EXECUTE format(
            'UPDATE course_chat_topics SET count = count + 1 WHERE course_id = %L AND id = %L RETURNING *',
            course_id, topic_id
        );
    END LOOP;
END;
$$;

ALTER FUNCTION "public"."increment_course_chat_topics"("course_id" bigint, "topic_ids" bigint[]) OWNER TO "postgres";

CREATE OR REPLACE FUNCTION "public"."match_documents"("query_embedding" "public"."vector", "match_count" integer DEFAULT NULL::integer, "filter" "jsonb" DEFAULT '{}'::"jsonb") RETURNS TABLE("id" bigint, "content" "text", "metadata" "jsonb", "similarity" double precision)
    LANGUAGE "plpgsql"
    AS $$
#variable_conflict use_column
begin
  return query
  select
    id,
    content,
    metadata,
    1 - (documents.embedding <=> query_embedding) as similarity
  from documents
  where metadata @> filter
  order by documents.embedding <=> query_embedding
  limit match_count;
end;
$$;

ALTER FUNCTION "public"."match_documents"("query_embedding" "public"."vector", "match_count" integer, "filter" "jsonb") OWNER TO "postgres";

CREATE OR REPLACE FUNCTION "public"."match_documents_by_course_id"("query_embedding" "public"."vector", "course_id_arg" integer, "match_count" integer DEFAULT NULL::integer) RETURNS TABLE("id" bigint, "content" "text", "metadata" "jsonb", "similarity" double precision)
    LANGUAGE "plpgsql"
    AS $$
#variable_conflict use_column
begin
  return query
  select
    id,
    content,
    metadata,
    1 - (documents.embedding <=> query_embedding) as similarity
  from documents
  where course_id = course_id_arg
  order by documents.embedding <=> query_embedding
  limit match_count;
end;
$$;

ALTER FUNCTION "public"."match_documents_by_course_id"("query_embedding" "public"."vector", "course_id_arg" integer, "match_count" integer) OWNER TO "postgres";

CREATE OR REPLACE FUNCTION "public"."match_documents_by_file_ids"("query_embedding" "public"."vector", "file_ids" integer[], "match_count" integer DEFAULT NULL::integer) RETURNS TABLE("id" bigint, "content" "text", "metadata" "jsonb", "similarity" double precision)
    LANGUAGE "plpgsql"
    AS $$
#variable_conflict use_column
begin
  return query
  select
    id,
    content,
    metadata,
    1 - (documents.embedding <=> query_embedding) as similarity
  from documents
  where (metadata ->> 'file_id')::int = ANY(file_ids)
  order by documents.embedding <=> query_embedding
  limit match_count;
end;
$$;

ALTER FUNCTION "public"."match_documents_by_file_ids"("query_embedding" "public"."vector", "file_ids" integer[], "match_count" integer) OWNER TO "postgres";

CREATE TABLE IF NOT EXISTS "public"."course_chat_messages" (
    "id" bigint NOT NULL,
    "created_at" timestamp with time zone DEFAULT "now"() NOT NULL,
    "chat_id" bigint NOT NULL,
    "role" "text" NOT NULL,
    "content" "text" NOT NULL,
    "metadata" "jsonb"
);

ALTER TABLE "public"."course_chat_messages" OWNER TO "postgres";

ALTER TABLE "public"."course_chat_messages" ALTER COLUMN "id" ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME "public"."course_chat_messages_id_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);

ALTER TABLE "public"."course_chat_misconceptions" ALTER COLUMN "id" ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME "public"."course_chat_misconceptions_id_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);

ALTER TABLE "public"."course_chat_topics" ALTER COLUMN "id" ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME "public"."course_chat_topics_id_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);

CREATE TABLE IF NOT EXISTS "public"."course_chats" (
    "id" bigint NOT NULL,
    "created_at" timestamp with time zone DEFAULT "now"() NOT NULL,
    "title" "text",
    "course_id" bigint,
    "member_id" bigint NOT NULL
);

ALTER TABLE "public"."course_chats" OWNER TO "postgres";

ALTER TABLE "public"."course_chats" ALTER COLUMN "id" ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME "public"."course_chats_id_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);

CREATE TABLE IF NOT EXISTS "public"."course_folders" (
    "id" bigint NOT NULL,
    "created_at" timestamp with time zone DEFAULT "now"() NOT NULL,
    "name" "text" NOT NULL,
    "course_id" bigint NOT NULL,
    "parent_id" bigint
);

ALTER TABLE "public"."course_folders" OWNER TO "postgres";

ALTER TABLE "public"."course_folders" ALTER COLUMN "id" ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME "public"."course_folders_id_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);

CREATE TABLE IF NOT EXISTS "public"."course_materials" (
    "id" bigint NOT NULL,
    "created_at" timestamp with time zone DEFAULT "now"() NOT NULL,
    "course_id" bigint NOT NULL,
    "name" "text" NOT NULL,
    "status" "text",
    "folder_id" bigint
);

ALTER TABLE "public"."course_materials" OWNER TO "postgres";

ALTER TABLE "public"."course_materials" ALTER COLUMN "id" ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME "public"."course_materials_id_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);

CREATE TABLE IF NOT EXISTS "public"."course_members" (
    "id" bigint NOT NULL,
    "created_at" timestamp with time zone DEFAULT "now"() NOT NULL,
    "course_id" bigint NOT NULL,
    "email" "text" NOT NULL,
    "role" "text" NOT NULL
);

ALTER TABLE "public"."course_members" OWNER TO "postgres";

ALTER TABLE "public"."course_members" ALTER COLUMN "id" ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME "public"."course_members_id_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);

CREATE TABLE IF NOT EXISTS "public"."courses" (
    "id" bigint NOT NULL,
    "created_at" timestamp with time zone DEFAULT "now"() NOT NULL,
    "title" "text" NOT NULL
);

ALTER TABLE "public"."courses" OWNER TO "postgres";

ALTER TABLE "public"."courses" ALTER COLUMN "id" ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME "public"."courses_id_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);

CREATE TABLE IF NOT EXISTS "public"."documents" (
    "id" bigint NOT NULL,
    "content" "text" NOT NULL,
    "metadata" "jsonb" NOT NULL,
    "embedding" "public"."vector"(1536) NOT NULL,
    "file_id" bigint NOT NULL,
    "course_id" bigint NOT NULL
);

ALTER TABLE "public"."documents" OWNER TO "postgres";

CREATE SEQUENCE IF NOT EXISTS "public"."documents_id_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

ALTER TABLE "public"."documents_id_seq" OWNER TO "postgres";

ALTER SEQUENCE "public"."documents_id_seq" OWNED BY "public"."documents"."id";

CREATE TABLE IF NOT EXISTS "public"."profiles" (
    "id" "uuid" NOT NULL,
    "updated_at" timestamp with time zone,
    "full_name" "text",
    "avatar_url" "text"
);

ALTER TABLE "public"."profiles" OWNER TO "postgres";

CREATE TABLE IF NOT EXISTS "public"."tool_chat_messages" (
    "id" bigint NOT NULL,
    "created_at" timestamp with time zone DEFAULT "now"() NOT NULL,
    "tool_chat_id" bigint,
    "role" "text",
    "content" "text",
    "metadata" "jsonb",
    "user_email" "text"
);

ALTER TABLE "public"."tool_chat_messages" OWNER TO "postgres";

ALTER TABLE "public"."tool_chat_messages" ALTER COLUMN "id" ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME "public"."tool_chat_messages_id_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);

CREATE TABLE IF NOT EXISTS "public"."tool_chats" (
    "id" bigint NOT NULL,
    "created_at" timestamp with time zone DEFAULT "now"() NOT NULL,
    "course_id" bigint,
    "title" "text",
    "tool_id" bigint
);

ALTER TABLE "public"."tool_chats" OWNER TO "postgres";

ALTER TABLE "public"."tool_chats" ALTER COLUMN "id" ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME "public"."tool_chats_id_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);

CREATE TABLE IF NOT EXISTS "public"."tools" (
    "id" bigint NOT NULL,
    "created_at" timestamp with time zone DEFAULT "now"() NOT NULL,
    "title" "text"
);

ALTER TABLE "public"."tools" OWNER TO "postgres";

ALTER TABLE "public"."tools" ALTER COLUMN "id" ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME "public"."tools_id_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);

ALTER TABLE ONLY "public"."documents" ALTER COLUMN "id" SET DEFAULT "nextval"('"public"."documents_id_seq"'::"regclass");

ALTER TABLE ONLY "public"."course_chat_messages"
    ADD CONSTRAINT "course_chat_messages_pkey" PRIMARY KEY ("id");

ALTER TABLE ONLY "public"."course_chat_misconceptions"
    ADD CONSTRAINT "course_chat_misconceptions_pkey" PRIMARY KEY ("id");

ALTER TABLE ONLY "public"."course_chat_topics"
    ADD CONSTRAINT "course_chat_topics_pkey" PRIMARY KEY ("id");

ALTER TABLE ONLY "public"."course_chats"
    ADD CONSTRAINT "course_chats_pkey" PRIMARY KEY ("id");

ALTER TABLE ONLY "public"."course_folders"
    ADD CONSTRAINT "course_folders_pkey" PRIMARY KEY ("id");

ALTER TABLE ONLY "public"."course_materials"
    ADD CONSTRAINT "course_materials_pkey" PRIMARY KEY ("id");

ALTER TABLE ONLY "public"."course_members"
    ADD CONSTRAINT "course_members_pkey" PRIMARY KEY ("id");

ALTER TABLE ONLY "public"."courses"
    ADD CONSTRAINT "courses_pkey" PRIMARY KEY ("id");

ALTER TABLE ONLY "public"."documents"
    ADD CONSTRAINT "documents_pkey" PRIMARY KEY ("id");

ALTER TABLE ONLY "public"."profiles"
    ADD CONSTRAINT "profiles_pkey" PRIMARY KEY ("id");

ALTER TABLE ONLY "public"."tool_chat_messages"
    ADD CONSTRAINT "tool_chat_messages_pkey" PRIMARY KEY ("id");

ALTER TABLE ONLY "public"."tool_chats"
    ADD CONSTRAINT "tool_chats_pkey" PRIMARY KEY ("id");

ALTER TABLE ONLY "public"."tools"
    ADD CONSTRAINT "tools_pkey" PRIMARY KEY ("id");

ALTER TABLE ONLY "public"."course_chat_misconceptions"
    ADD CONSTRAINT "course_chat_misconceptions_course_id_fkey" FOREIGN KEY ("course_id") REFERENCES "public"."courses"("id");

ALTER TABLE ONLY "public"."course_chat_topics"
    ADD CONSTRAINT "course_chat_topics_course_id_fkey" FOREIGN KEY ("course_id") REFERENCES "public"."courses"("id");

ALTER TABLE ONLY "public"."course_folders"
    ADD CONSTRAINT "course_folders_course_id_fkey" FOREIGN KEY ("course_id") REFERENCES "public"."courses"("id");

ALTER TABLE ONLY "public"."course_members"
    ADD CONSTRAINT "course_members_course_id_fkey" FOREIGN KEY ("course_id") REFERENCES "public"."courses"("id");

ALTER TABLE ONLY "public"."documents"
    ADD CONSTRAINT "documents_course_id_fkey" FOREIGN KEY ("course_id") REFERENCES "public"."courses"("id");

ALTER TABLE ONLY "public"."profiles"
    ADD CONSTRAINT "profiles_id_fkey" FOREIGN KEY ("id") REFERENCES "auth"."users"("id") ON DELETE CASCADE;

ALTER TABLE ONLY "public"."course_chat_messages"
    ADD CONSTRAINT "public_course_chat_messages_chat_id_fkey" FOREIGN KEY ("chat_id") REFERENCES "public"."course_chats"("id");

ALTER TABLE ONLY "public"."course_chats"
    ADD CONSTRAINT "public_course_chats_course_id_fkey" FOREIGN KEY ("course_id") REFERENCES "public"."courses"("id") ON DELETE CASCADE;

ALTER TABLE ONLY "public"."course_chats"
    ADD CONSTRAINT "public_course_chats_member_id_fkey" FOREIGN KEY ("member_id") REFERENCES "public"."course_members"("id");

ALTER TABLE ONLY "public"."course_folders"
    ADD CONSTRAINT "public_course_folders_parent_id_fkey" FOREIGN KEY ("parent_id") REFERENCES "public"."course_folders"("id") ON DELETE CASCADE;

ALTER TABLE ONLY "public"."course_materials"
    ADD CONSTRAINT "public_course_materials_course_id_fkey" FOREIGN KEY ("course_id") REFERENCES "public"."courses"("id") ON DELETE CASCADE;

ALTER TABLE ONLY "public"."course_materials"
    ADD CONSTRAINT "public_course_materials_folder_id_fkey" FOREIGN KEY ("folder_id") REFERENCES "public"."course_folders"("id") ON DELETE CASCADE;

ALTER TABLE ONLY "public"."documents"
    ADD CONSTRAINT "public_documents_file_id_fkey" FOREIGN KEY ("file_id") REFERENCES "public"."course_materials"("id") ON DELETE CASCADE;

ALTER TABLE ONLY "public"."tool_chat_messages"
    ADD CONSTRAINT "public_tool_chat_messages_tool_chat_id_fkey" FOREIGN KEY ("tool_chat_id") REFERENCES "public"."tool_chats"("id");

ALTER TABLE ONLY "public"."tool_chats"
    ADD CONSTRAINT "public_tool_chats_course_id_fkey" FOREIGN KEY ("course_id") REFERENCES "public"."courses"("id");

ALTER TABLE ONLY "public"."tool_chats"
    ADD CONSTRAINT "public_tool_chats_tool_id_fkey" FOREIGN KEY ("tool_id") REFERENCES "public"."tools"("id");

CREATE POLICY "Public profiles are viewable by everyone." ON "public"."profiles" FOR SELECT USING (true);

CREATE POLICY "Users can insert their own profile." ON "public"."profiles" FOR INSERT WITH CHECK (("auth"."uid"() = "id"));

CREATE POLICY "Users can update own profile." ON "public"."profiles" FOR UPDATE USING (("auth"."uid"() = "id"));

ALTER TABLE "public"."course_chat_messages" ENABLE ROW LEVEL SECURITY;

ALTER TABLE "public"."course_chat_misconceptions" ENABLE ROW LEVEL SECURITY;

ALTER TABLE "public"."course_chat_topics" ENABLE ROW LEVEL SECURITY;

ALTER TABLE "public"."course_chats" ENABLE ROW LEVEL SECURITY;

ALTER TABLE "public"."course_folders" ENABLE ROW LEVEL SECURITY;

ALTER TABLE "public"."course_materials" ENABLE ROW LEVEL SECURITY;

ALTER TABLE "public"."course_members" ENABLE ROW LEVEL SECURITY;

ALTER TABLE "public"."courses" ENABLE ROW LEVEL SECURITY;

ALTER TABLE "public"."documents" ENABLE ROW LEVEL SECURITY;

ALTER TABLE "public"."profiles" ENABLE ROW LEVEL SECURITY;

ALTER TABLE "public"."tool_chat_messages" ENABLE ROW LEVEL SECURITY;

ALTER TABLE "public"."tool_chats" ENABLE ROW LEVEL SECURITY;

ALTER TABLE "public"."tools" ENABLE ROW LEVEL SECURITY;

ALTER PUBLICATION "supabase_realtime" OWNER TO "postgres";

GRANT USAGE ON SCHEMA "public" TO "postgres";
GRANT USAGE ON SCHEMA "public" TO "anon";
GRANT USAGE ON SCHEMA "public" TO "authenticated";
GRANT USAGE ON SCHEMA "public" TO "service_role";

GRANT ALL ON FUNCTION "public"."vector_in"("cstring", "oid", integer) TO "postgres";
GRANT ALL ON FUNCTION "public"."vector_in"("cstring", "oid", integer) TO "anon";
GRANT ALL ON FUNCTION "public"."vector_in"("cstring", "oid", integer) TO "authenticated";
GRANT ALL ON FUNCTION "public"."vector_in"("cstring", "oid", integer) TO "service_role";

GRANT ALL ON FUNCTION "public"."vector_out"("public"."vector") TO "postgres";
GRANT ALL ON FUNCTION "public"."vector_out"("public"."vector") TO "anon";
GRANT ALL ON FUNCTION "public"."vector_out"("public"."vector") TO "authenticated";
GRANT ALL ON FUNCTION "public"."vector_out"("public"."vector") TO "service_role";

GRANT ALL ON FUNCTION "public"."vector_recv"("internal", "oid", integer) TO "postgres";
GRANT ALL ON FUNCTION "public"."vector_recv"("internal", "oid", integer) TO "anon";
GRANT ALL ON FUNCTION "public"."vector_recv"("internal", "oid", integer) TO "authenticated";
GRANT ALL ON FUNCTION "public"."vector_recv"("internal", "oid", integer) TO "service_role";

GRANT ALL ON FUNCTION "public"."vector_send"("public"."vector") TO "postgres";
GRANT ALL ON FUNCTION "public"."vector_send"("public"."vector") TO "anon";
GRANT ALL ON FUNCTION "public"."vector_send"("public"."vector") TO "authenticated";
GRANT ALL ON FUNCTION "public"."vector_send"("public"."vector") TO "service_role";

GRANT ALL ON FUNCTION "public"."vector_typmod_in"("cstring"[]) TO "postgres";
GRANT ALL ON FUNCTION "public"."vector_typmod_in"("cstring"[]) TO "anon";
GRANT ALL ON FUNCTION "public"."vector_typmod_in"("cstring"[]) TO "authenticated";
GRANT ALL ON FUNCTION "public"."vector_typmod_in"("cstring"[]) TO "service_role";

GRANT ALL ON FUNCTION "public"."array_to_vector"(real[], integer, boolean) TO "postgres";
GRANT ALL ON FUNCTION "public"."array_to_vector"(real[], integer, boolean) TO "anon";
GRANT ALL ON FUNCTION "public"."array_to_vector"(real[], integer, boolean) TO "authenticated";
GRANT ALL ON FUNCTION "public"."array_to_vector"(real[], integer, boolean) TO "service_role";

GRANT ALL ON FUNCTION "public"."array_to_vector"(double precision[], integer, boolean) TO "postgres";
GRANT ALL ON FUNCTION "public"."array_to_vector"(double precision[], integer, boolean) TO "anon";
GRANT ALL ON FUNCTION "public"."array_to_vector"(double precision[], integer, boolean) TO "authenticated";
GRANT ALL ON FUNCTION "public"."array_to_vector"(double precision[], integer, boolean) TO "service_role";

GRANT ALL ON FUNCTION "public"."array_to_vector"(integer[], integer, boolean) TO "postgres";
GRANT ALL ON FUNCTION "public"."array_to_vector"(integer[], integer, boolean) TO "anon";
GRANT ALL ON FUNCTION "public"."array_to_vector"(integer[], integer, boolean) TO "authenticated";
GRANT ALL ON FUNCTION "public"."array_to_vector"(integer[], integer, boolean) TO "service_role";

GRANT ALL ON FUNCTION "public"."array_to_vector"(numeric[], integer, boolean) TO "postgres";
GRANT ALL ON FUNCTION "public"."array_to_vector"(numeric[], integer, boolean) TO "anon";
GRANT ALL ON FUNCTION "public"."array_to_vector"(numeric[], integer, boolean) TO "authenticated";
GRANT ALL ON FUNCTION "public"."array_to_vector"(numeric[], integer, boolean) TO "service_role";

GRANT ALL ON FUNCTION "public"."vector_to_float4"("public"."vector", integer, boolean) TO "postgres";
GRANT ALL ON FUNCTION "public"."vector_to_float4"("public"."vector", integer, boolean) TO "anon";
GRANT ALL ON FUNCTION "public"."vector_to_float4"("public"."vector", integer, boolean) TO "authenticated";
GRANT ALL ON FUNCTION "public"."vector_to_float4"("public"."vector", integer, boolean) TO "service_role";

GRANT ALL ON FUNCTION "public"."vector"("public"."vector", integer, boolean) TO "postgres";
GRANT ALL ON FUNCTION "public"."vector"("public"."vector", integer, boolean) TO "anon";
GRANT ALL ON FUNCTION "public"."vector"("public"."vector", integer, boolean) TO "authenticated";
GRANT ALL ON FUNCTION "public"."vector"("public"."vector", integer, boolean) TO "service_role";

GRANT ALL ON FUNCTION "public"."cosine_distance"("public"."vector", "public"."vector") TO "postgres";
GRANT ALL ON FUNCTION "public"."cosine_distance"("public"."vector", "public"."vector") TO "anon";
GRANT ALL ON FUNCTION "public"."cosine_distance"("public"."vector", "public"."vector") TO "authenticated";
GRANT ALL ON FUNCTION "public"."cosine_distance"("public"."vector", "public"."vector") TO "service_role";

GRANT ALL ON FUNCTION "public"."handle_new_user"() TO "anon";
GRANT ALL ON FUNCTION "public"."handle_new_user"() TO "authenticated";
GRANT ALL ON FUNCTION "public"."handle_new_user"() TO "service_role";

GRANT ALL ON FUNCTION "public"."hnswhandler"("internal") TO "postgres";
GRANT ALL ON FUNCTION "public"."hnswhandler"("internal") TO "anon";
GRANT ALL ON FUNCTION "public"."hnswhandler"("internal") TO "authenticated";
GRANT ALL ON FUNCTION "public"."hnswhandler"("internal") TO "service_role";

GRANT ALL ON FUNCTION "public"."increment_column"("table_name" "text", "column_name" "text", "amount" bigint) TO "anon";
GRANT ALL ON FUNCTION "public"."increment_column"("table_name" "text", "column_name" "text", "amount" bigint) TO "authenticated";
GRANT ALL ON FUNCTION "public"."increment_column"("table_name" "text", "column_name" "text", "amount" bigint) TO "service_role";

GRANT ALL ON TABLE "public"."course_chat_misconceptions" TO "anon";
GRANT ALL ON TABLE "public"."course_chat_misconceptions" TO "authenticated";
GRANT ALL ON TABLE "public"."course_chat_misconceptions" TO "service_role";

GRANT ALL ON FUNCTION "public"."increment_course_chat_misconceptions"("course_id" bigint, "misconception_ids" bigint[]) TO "anon";
GRANT ALL ON FUNCTION "public"."increment_course_chat_misconceptions"("course_id" bigint, "misconception_ids" bigint[]) TO "authenticated";
GRANT ALL ON FUNCTION "public"."increment_course_chat_misconceptions"("course_id" bigint, "misconception_ids" bigint[]) TO "service_role";

GRANT ALL ON FUNCTION "public"."increment_course_chat_topic"("course_id" bigint, "topic_id" bigint) TO "anon";
GRANT ALL ON FUNCTION "public"."increment_course_chat_topic"("course_id" bigint, "topic_id" bigint) TO "authenticated";
GRANT ALL ON FUNCTION "public"."increment_course_chat_topic"("course_id" bigint, "topic_id" bigint) TO "service_role";

GRANT ALL ON TABLE "public"."course_chat_topics" TO "anon";
GRANT ALL ON TABLE "public"."course_chat_topics" TO "authenticated";
GRANT ALL ON TABLE "public"."course_chat_topics" TO "service_role";

GRANT ALL ON FUNCTION "public"."increment_course_chat_topics"("course_id" bigint, "topic_ids" bigint[]) TO "anon";
GRANT ALL ON FUNCTION "public"."increment_course_chat_topics"("course_id" bigint, "topic_ids" bigint[]) TO "authenticated";
GRANT ALL ON FUNCTION "public"."increment_course_chat_topics"("course_id" bigint, "topic_ids" bigint[]) TO "service_role";

GRANT ALL ON FUNCTION "public"."inner_product"("public"."vector", "public"."vector") TO "postgres";
GRANT ALL ON FUNCTION "public"."inner_product"("public"."vector", "public"."vector") TO "anon";
GRANT ALL ON FUNCTION "public"."inner_product"("public"."vector", "public"."vector") TO "authenticated";
GRANT ALL ON FUNCTION "public"."inner_product"("public"."vector", "public"."vector") TO "service_role";

GRANT ALL ON FUNCTION "public"."ivfflathandler"("internal") TO "postgres";
GRANT ALL ON FUNCTION "public"."ivfflathandler"("internal") TO "anon";
GRANT ALL ON FUNCTION "public"."ivfflathandler"("internal") TO "authenticated";
GRANT ALL ON FUNCTION "public"."ivfflathandler"("internal") TO "service_role";

GRANT ALL ON FUNCTION "public"."l1_distance"("public"."vector", "public"."vector") TO "postgres";
GRANT ALL ON FUNCTION "public"."l1_distance"("public"."vector", "public"."vector") TO "anon";
GRANT ALL ON FUNCTION "public"."l1_distance"("public"."vector", "public"."vector") TO "authenticated";
GRANT ALL ON FUNCTION "public"."l1_distance"("public"."vector", "public"."vector") TO "service_role";

GRANT ALL ON FUNCTION "public"."l2_distance"("public"."vector", "public"."vector") TO "postgres";
GRANT ALL ON FUNCTION "public"."l2_distance"("public"."vector", "public"."vector") TO "anon";
GRANT ALL ON FUNCTION "public"."l2_distance"("public"."vector", "public"."vector") TO "authenticated";
GRANT ALL ON FUNCTION "public"."l2_distance"("public"."vector", "public"."vector") TO "service_role";

GRANT ALL ON FUNCTION "public"."match_documents"("query_embedding" "public"."vector", "match_count" integer, "filter" "jsonb") TO "anon";
GRANT ALL ON FUNCTION "public"."match_documents"("query_embedding" "public"."vector", "match_count" integer, "filter" "jsonb") TO "authenticated";
GRANT ALL ON FUNCTION "public"."match_documents"("query_embedding" "public"."vector", "match_count" integer, "filter" "jsonb") TO "service_role";

GRANT ALL ON FUNCTION "public"."match_documents_by_course_id"("query_embedding" "public"."vector", "course_id_arg" integer, "match_count" integer) TO "anon";
GRANT ALL ON FUNCTION "public"."match_documents_by_course_id"("query_embedding" "public"."vector", "course_id_arg" integer, "match_count" integer) TO "authenticated";
GRANT ALL ON FUNCTION "public"."match_documents_by_course_id"("query_embedding" "public"."vector", "course_id_arg" integer, "match_count" integer) TO "service_role";

GRANT ALL ON FUNCTION "public"."match_documents_by_file_ids"("query_embedding" "public"."vector", "file_ids" integer[], "match_count" integer) TO "anon";
GRANT ALL ON FUNCTION "public"."match_documents_by_file_ids"("query_embedding" "public"."vector", "file_ids" integer[], "match_count" integer) TO "authenticated";
GRANT ALL ON FUNCTION "public"."match_documents_by_file_ids"("query_embedding" "public"."vector", "file_ids" integer[], "match_count" integer) TO "service_role";

GRANT ALL ON FUNCTION "public"."vector_accum"(double precision[], "public"."vector") TO "postgres";
GRANT ALL ON FUNCTION "public"."vector_accum"(double precision[], "public"."vector") TO "anon";
GRANT ALL ON FUNCTION "public"."vector_accum"(double precision[], "public"."vector") TO "authenticated";
GRANT ALL ON FUNCTION "public"."vector_accum"(double precision[], "public"."vector") TO "service_role";

GRANT ALL ON FUNCTION "public"."vector_add"("public"."vector", "public"."vector") TO "postgres";
GRANT ALL ON FUNCTION "public"."vector_add"("public"."vector", "public"."vector") TO "anon";
GRANT ALL ON FUNCTION "public"."vector_add"("public"."vector", "public"."vector") TO "authenticated";
GRANT ALL ON FUNCTION "public"."vector_add"("public"."vector", "public"."vector") TO "service_role";

GRANT ALL ON FUNCTION "public"."vector_avg"(double precision[]) TO "postgres";
GRANT ALL ON FUNCTION "public"."vector_avg"(double precision[]) TO "anon";
GRANT ALL ON FUNCTION "public"."vector_avg"(double precision[]) TO "authenticated";
GRANT ALL ON FUNCTION "public"."vector_avg"(double precision[]) TO "service_role";

GRANT ALL ON FUNCTION "public"."vector_cmp"("public"."vector", "public"."vector") TO "postgres";
GRANT ALL ON FUNCTION "public"."vector_cmp"("public"."vector", "public"."vector") TO "anon";
GRANT ALL ON FUNCTION "public"."vector_cmp"("public"."vector", "public"."vector") TO "authenticated";
GRANT ALL ON FUNCTION "public"."vector_cmp"("public"."vector", "public"."vector") TO "service_role";

GRANT ALL ON FUNCTION "public"."vector_combine"(double precision[], double precision[]) TO "postgres";
GRANT ALL ON FUNCTION "public"."vector_combine"(double precision[], double precision[]) TO "anon";
GRANT ALL ON FUNCTION "public"."vector_combine"(double precision[], double precision[]) TO "authenticated";
GRANT ALL ON FUNCTION "public"."vector_combine"(double precision[], double precision[]) TO "service_role";

GRANT ALL ON FUNCTION "public"."vector_dims"("public"."vector") TO "postgres";
GRANT ALL ON FUNCTION "public"."vector_dims"("public"."vector") TO "anon";
GRANT ALL ON FUNCTION "public"."vector_dims"("public"."vector") TO "authenticated";
GRANT ALL ON FUNCTION "public"."vector_dims"("public"."vector") TO "service_role";

GRANT ALL ON FUNCTION "public"."vector_eq"("public"."vector", "public"."vector") TO "postgres";
GRANT ALL ON FUNCTION "public"."vector_eq"("public"."vector", "public"."vector") TO "anon";
GRANT ALL ON FUNCTION "public"."vector_eq"("public"."vector", "public"."vector") TO "authenticated";
GRANT ALL ON FUNCTION "public"."vector_eq"("public"."vector", "public"."vector") TO "service_role";

GRANT ALL ON FUNCTION "public"."vector_ge"("public"."vector", "public"."vector") TO "postgres";
GRANT ALL ON FUNCTION "public"."vector_ge"("public"."vector", "public"."vector") TO "anon";
GRANT ALL ON FUNCTION "public"."vector_ge"("public"."vector", "public"."vector") TO "authenticated";
GRANT ALL ON FUNCTION "public"."vector_ge"("public"."vector", "public"."vector") TO "service_role";

GRANT ALL ON FUNCTION "public"."vector_gt"("public"."vector", "public"."vector") TO "postgres";
GRANT ALL ON FUNCTION "public"."vector_gt"("public"."vector", "public"."vector") TO "anon";
GRANT ALL ON FUNCTION "public"."vector_gt"("public"."vector", "public"."vector") TO "authenticated";
GRANT ALL ON FUNCTION "public"."vector_gt"("public"."vector", "public"."vector") TO "service_role";

GRANT ALL ON FUNCTION "public"."vector_l2_squared_distance"("public"."vector", "public"."vector") TO "postgres";
GRANT ALL ON FUNCTION "public"."vector_l2_squared_distance"("public"."vector", "public"."vector") TO "anon";
GRANT ALL ON FUNCTION "public"."vector_l2_squared_distance"("public"."vector", "public"."vector") TO "authenticated";
GRANT ALL ON FUNCTION "public"."vector_l2_squared_distance"("public"."vector", "public"."vector") TO "service_role";

GRANT ALL ON FUNCTION "public"."vector_le"("public"."vector", "public"."vector") TO "postgres";
GRANT ALL ON FUNCTION "public"."vector_le"("public"."vector", "public"."vector") TO "anon";
GRANT ALL ON FUNCTION "public"."vector_le"("public"."vector", "public"."vector") TO "authenticated";
GRANT ALL ON FUNCTION "public"."vector_le"("public"."vector", "public"."vector") TO "service_role";

GRANT ALL ON FUNCTION "public"."vector_lt"("public"."vector", "public"."vector") TO "postgres";
GRANT ALL ON FUNCTION "public"."vector_lt"("public"."vector", "public"."vector") TO "anon";
GRANT ALL ON FUNCTION "public"."vector_lt"("public"."vector", "public"."vector") TO "authenticated";
GRANT ALL ON FUNCTION "public"."vector_lt"("public"."vector", "public"."vector") TO "service_role";

GRANT ALL ON FUNCTION "public"."vector_mul"("public"."vector", "public"."vector") TO "postgres";
GRANT ALL ON FUNCTION "public"."vector_mul"("public"."vector", "public"."vector") TO "anon";
GRANT ALL ON FUNCTION "public"."vector_mul"("public"."vector", "public"."vector") TO "authenticated";
GRANT ALL ON FUNCTION "public"."vector_mul"("public"."vector", "public"."vector") TO "service_role";

GRANT ALL ON FUNCTION "public"."vector_ne"("public"."vector", "public"."vector") TO "postgres";
GRANT ALL ON FUNCTION "public"."vector_ne"("public"."vector", "public"."vector") TO "anon";
GRANT ALL ON FUNCTION "public"."vector_ne"("public"."vector", "public"."vector") TO "authenticated";
GRANT ALL ON FUNCTION "public"."vector_ne"("public"."vector", "public"."vector") TO "service_role";

GRANT ALL ON FUNCTION "public"."vector_negative_inner_product"("public"."vector", "public"."vector") TO "postgres";
GRANT ALL ON FUNCTION "public"."vector_negative_inner_product"("public"."vector", "public"."vector") TO "anon";
GRANT ALL ON FUNCTION "public"."vector_negative_inner_product"("public"."vector", "public"."vector") TO "authenticated";
GRANT ALL ON FUNCTION "public"."vector_negative_inner_product"("public"."vector", "public"."vector") TO "service_role";

GRANT ALL ON FUNCTION "public"."vector_norm"("public"."vector") TO "postgres";
GRANT ALL ON FUNCTION "public"."vector_norm"("public"."vector") TO "anon";
GRANT ALL ON FUNCTION "public"."vector_norm"("public"."vector") TO "authenticated";
GRANT ALL ON FUNCTION "public"."vector_norm"("public"."vector") TO "service_role";

GRANT ALL ON FUNCTION "public"."vector_spherical_distance"("public"."vector", "public"."vector") TO "postgres";
GRANT ALL ON FUNCTION "public"."vector_spherical_distance"("public"."vector", "public"."vector") TO "anon";
GRANT ALL ON FUNCTION "public"."vector_spherical_distance"("public"."vector", "public"."vector") TO "authenticated";
GRANT ALL ON FUNCTION "public"."vector_spherical_distance"("public"."vector", "public"."vector") TO "service_role";

GRANT ALL ON FUNCTION "public"."vector_sub"("public"."vector", "public"."vector") TO "postgres";
GRANT ALL ON FUNCTION "public"."vector_sub"("public"."vector", "public"."vector") TO "anon";
GRANT ALL ON FUNCTION "public"."vector_sub"("public"."vector", "public"."vector") TO "authenticated";
GRANT ALL ON FUNCTION "public"."vector_sub"("public"."vector", "public"."vector") TO "service_role";

GRANT ALL ON FUNCTION "public"."avg"("public"."vector") TO "postgres";
GRANT ALL ON FUNCTION "public"."avg"("public"."vector") TO "anon";
GRANT ALL ON FUNCTION "public"."avg"("public"."vector") TO "authenticated";
GRANT ALL ON FUNCTION "public"."avg"("public"."vector") TO "service_role";

GRANT ALL ON FUNCTION "public"."sum"("public"."vector") TO "postgres";
GRANT ALL ON FUNCTION "public"."sum"("public"."vector") TO "anon";
GRANT ALL ON FUNCTION "public"."sum"("public"."vector") TO "authenticated";
GRANT ALL ON FUNCTION "public"."sum"("public"."vector") TO "service_role";

GRANT ALL ON TABLE "public"."course_chat_messages" TO "anon";
GRANT ALL ON TABLE "public"."course_chat_messages" TO "authenticated";
GRANT ALL ON TABLE "public"."course_chat_messages" TO "service_role";

GRANT ALL ON SEQUENCE "public"."course_chat_messages_id_seq" TO "anon";
GRANT ALL ON SEQUENCE "public"."course_chat_messages_id_seq" TO "authenticated";
GRANT ALL ON SEQUENCE "public"."course_chat_messages_id_seq" TO "service_role";

GRANT ALL ON SEQUENCE "public"."course_chat_misconceptions_id_seq" TO "anon";
GRANT ALL ON SEQUENCE "public"."course_chat_misconceptions_id_seq" TO "authenticated";
GRANT ALL ON SEQUENCE "public"."course_chat_misconceptions_id_seq" TO "service_role";

GRANT ALL ON SEQUENCE "public"."course_chat_topics_id_seq" TO "anon";
GRANT ALL ON SEQUENCE "public"."course_chat_topics_id_seq" TO "authenticated";
GRANT ALL ON SEQUENCE "public"."course_chat_topics_id_seq" TO "service_role";

GRANT ALL ON TABLE "public"."course_chats" TO "anon";
GRANT ALL ON TABLE "public"."course_chats" TO "authenticated";
GRANT ALL ON TABLE "public"."course_chats" TO "service_role";

GRANT ALL ON SEQUENCE "public"."course_chats_id_seq" TO "anon";
GRANT ALL ON SEQUENCE "public"."course_chats_id_seq" TO "authenticated";
GRANT ALL ON SEQUENCE "public"."course_chats_id_seq" TO "service_role";

GRANT ALL ON TABLE "public"."course_folders" TO "anon";
GRANT ALL ON TABLE "public"."course_folders" TO "authenticated";
GRANT ALL ON TABLE "public"."course_folders" TO "service_role";

GRANT ALL ON SEQUENCE "public"."course_folders_id_seq" TO "anon";
GRANT ALL ON SEQUENCE "public"."course_folders_id_seq" TO "authenticated";
GRANT ALL ON SEQUENCE "public"."course_folders_id_seq" TO "service_role";

GRANT ALL ON TABLE "public"."course_materials" TO "anon";
GRANT ALL ON TABLE "public"."course_materials" TO "authenticated";
GRANT ALL ON TABLE "public"."course_materials" TO "service_role";

GRANT ALL ON SEQUENCE "public"."course_materials_id_seq" TO "anon";
GRANT ALL ON SEQUENCE "public"."course_materials_id_seq" TO "authenticated";
GRANT ALL ON SEQUENCE "public"."course_materials_id_seq" TO "service_role";

GRANT ALL ON TABLE "public"."course_members" TO "anon";
GRANT ALL ON TABLE "public"."course_members" TO "authenticated";
GRANT ALL ON TABLE "public"."course_members" TO "service_role";

GRANT ALL ON SEQUENCE "public"."course_members_id_seq" TO "anon";
GRANT ALL ON SEQUENCE "public"."course_members_id_seq" TO "authenticated";
GRANT ALL ON SEQUENCE "public"."course_members_id_seq" TO "service_role";

GRANT ALL ON TABLE "public"."courses" TO "anon";
GRANT ALL ON TABLE "public"."courses" TO "authenticated";
GRANT ALL ON TABLE "public"."courses" TO "service_role";

GRANT ALL ON SEQUENCE "public"."courses_id_seq" TO "anon";
GRANT ALL ON SEQUENCE "public"."courses_id_seq" TO "authenticated";
GRANT ALL ON SEQUENCE "public"."courses_id_seq" TO "service_role";

GRANT ALL ON TABLE "public"."documents" TO "anon";
GRANT ALL ON TABLE "public"."documents" TO "authenticated";
GRANT ALL ON TABLE "public"."documents" TO "service_role";

GRANT ALL ON SEQUENCE "public"."documents_id_seq" TO "anon";
GRANT ALL ON SEQUENCE "public"."documents_id_seq" TO "authenticated";
GRANT ALL ON SEQUENCE "public"."documents_id_seq" TO "service_role";

GRANT ALL ON TABLE "public"."profiles" TO "anon";
GRANT ALL ON TABLE "public"."profiles" TO "authenticated";
GRANT ALL ON TABLE "public"."profiles" TO "service_role";

GRANT ALL ON TABLE "public"."tool_chat_messages" TO "anon";
GRANT ALL ON TABLE "public"."tool_chat_messages" TO "authenticated";
GRANT ALL ON TABLE "public"."tool_chat_messages" TO "service_role";

GRANT ALL ON SEQUENCE "public"."tool_chat_messages_id_seq" TO "anon";
GRANT ALL ON SEQUENCE "public"."tool_chat_messages_id_seq" TO "authenticated";
GRANT ALL ON SEQUENCE "public"."tool_chat_messages_id_seq" TO "service_role";

GRANT ALL ON TABLE "public"."tool_chats" TO "anon";
GRANT ALL ON TABLE "public"."tool_chats" TO "authenticated";
GRANT ALL ON TABLE "public"."tool_chats" TO "service_role";

GRANT ALL ON SEQUENCE "public"."tool_chats_id_seq" TO "anon";
GRANT ALL ON SEQUENCE "public"."tool_chats_id_seq" TO "authenticated";
GRANT ALL ON SEQUENCE "public"."tool_chats_id_seq" TO "service_role";

GRANT ALL ON TABLE "public"."tools" TO "anon";
GRANT ALL ON TABLE "public"."tools" TO "authenticated";
GRANT ALL ON TABLE "public"."tools" TO "service_role";

GRANT ALL ON SEQUENCE "public"."tools_id_seq" TO "anon";
GRANT ALL ON SEQUENCE "public"."tools_id_seq" TO "authenticated";
GRANT ALL ON SEQUENCE "public"."tools_id_seq" TO "service_role";

ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON SEQUENCES  TO "postgres";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON SEQUENCES  TO "anon";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON SEQUENCES  TO "authenticated";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON SEQUENCES  TO "service_role";

ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON FUNCTIONS  TO "postgres";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON FUNCTIONS  TO "anon";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON FUNCTIONS  TO "authenticated";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON FUNCTIONS  TO "service_role";

ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON TABLES  TO "postgres";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON TABLES  TO "anon";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON TABLES  TO "authenticated";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON TABLES  TO "service_role";

RESET ALL;
