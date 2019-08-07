--
-- PostgreSQL database dump
--

-- Dumped from database version 11.4 (Debian 11.4-1.pgdg90+1)
-- Dumped by pg_dump version 11.4 (Debian 11.4-1.pgdg90+1)

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

--
-- Name: dr; Type: SCHEMA; Schema: -; Owner: dbo
--

CREATE SCHEMA dr;


ALTER SCHEMA dr OWNER TO dbo;

--
-- Name: SCHEMA dr; Type: COMMENT; Schema: -; Owner: dbo
--

COMMENT ON SCHEMA dr IS 'Contains all the objects needed to operate the dr application';


SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: request_status; Type: TABLE; Schema: dr; Owner: dbo
--

CREATE TABLE dr.request_status (
    job_id bigint NOT NULL,
    request_id character varying(50) NOT NULL,
    granule_id character varying(100) NOT NULL,
    object_key character varying(255) NOT NULL,
    job_type character varying(12) DEFAULT 'restore'::character varying,
    restore_bucket_dest character varying(100),
    job_status character varying(12) DEFAULT 'inprogress'::character varying,
    request_time timestamp with time zone NOT NULL,
    last_update_time timestamp with time zone NOT NULL,
    CONSTRAINT request_status_job_status_check CHECK (((job_status)::text = ANY ((ARRAY['inprogress'::character varying, 'complete'::character varying, 'error'::character varying])::text[]))),
    CONSTRAINT request_status_job_type_check CHECK (((job_type)::text = ANY ((ARRAY['restore'::character varying, 'regenerate'::character varying])::text[])))
);


ALTER TABLE dr.request_status OWNER TO dbo;

--
-- Name: TABLE request_status; Type: COMMENT; Schema: dr; Owner: dbo
--

COMMENT ON TABLE dr.request_status IS 'Disaster recovery jobs status table';


--
-- Name: COLUMN request_status.job_id; Type: COMMENT; Schema: dr; Owner: dbo
--

COMMENT ON COLUMN dr.request_status.job_id IS 'unique job identifier';


--
-- Name: COLUMN request_status.request_id; Type: COMMENT; Schema: dr; Owner: dbo
--

COMMENT ON COLUMN dr.request_status.request_id IS 'request identifier assigned to all objects being requested for the granule';


--
-- Name: COLUMN request_status.granule_id; Type: COMMENT; Schema: dr; Owner: dbo
--

COMMENT ON COLUMN dr.request_status.granule_id IS 'granule id of the granule being restored';


--
-- Name: COLUMN request_status.object_key; Type: COMMENT; Schema: dr; Owner: dbo
--

COMMENT ON COLUMN dr.request_status.object_key IS 'object key being restored';


--
-- Name: COLUMN request_status.job_type; Type: COMMENT; Schema: dr; Owner: dbo
--

COMMENT ON COLUMN dr.request_status.job_type IS 'type of restore request that was made';


--
-- Name: COLUMN request_status.restore_bucket_dest; Type: COMMENT; Schema: dr; Owner: dbo
--

COMMENT ON COLUMN dr.request_status.restore_bucket_dest IS 'S3 bucket to restore the file to';


--
-- Name: COLUMN request_status.job_status; Type: COMMENT; Schema: dr; Owner: dbo
--

COMMENT ON COLUMN dr.request_status.job_status IS 'current status of the request';


--
-- Name: COLUMN request_status.request_time; Type: COMMENT; Schema: dr; Owner: dbo
--

COMMENT ON COLUMN dr.request_status.request_time IS 'Time the request was made';


--
-- Name: COLUMN request_status.last_update_time; Type: COMMENT; Schema: dr; Owner: dbo
--

COMMENT ON COLUMN dr.request_status.last_update_time IS 'The last time the request was updated';


--
-- Name: request_status_job_id_seq; Type: SEQUENCE; Schema: dr; Owner: dbo
--

CREATE SEQUENCE dr.request_status_job_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE dr.request_status_job_id_seq OWNER TO dbo;

--
-- Name: request_status_job_id_seq; Type: SEQUENCE OWNED BY; Schema: dr; Owner: dbo
--

ALTER SEQUENCE dr.request_status_job_id_seq OWNED BY dr.request_status.job_id;


--
-- Name: request_status job_id; Type: DEFAULT; Schema: dr; Owner: dbo
--

ALTER TABLE ONLY dr.request_status ALTER COLUMN job_id SET DEFAULT nextval('dr.request_status_job_id_seq'::regclass);


--
-- Name: request_status request_status_pkey; Type: CONSTRAINT; Schema: dr; Owner: dbo
--

ALTER TABLE ONLY dr.request_status
    ADD CONSTRAINT request_status_pkey PRIMARY KEY (job_id);


--
-- Name: idx_reqstat_keystatus; Type: INDEX; Schema: dr; Owner: dbo
--

CREATE INDEX idx_reqstat_keystatus ON dr.request_status USING btree (object_key, job_status);


--
-- Name: idx_reqstat_reqidgranid; Type: INDEX; Schema: dr; Owner: dbo
--

CREATE INDEX idx_reqstat_reqidgranid ON dr.request_status USING btree (request_id, granule_id);


--
-- Name: SCHEMA dr; Type: ACL; Schema: -; Owner: dbo
--

GRANT USAGE ON SCHEMA dr TO dr_role;


--
-- Name: TABLE request_status; Type: ACL; Schema: dr; Owner: dbo
--

GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,UPDATE ON TABLE dr.request_status TO dr_role;


--
-- Name: SEQUENCE request_status_job_id_seq; Type: ACL; Schema: dr; Owner: dbo
--

GRANT ALL ON SEQUENCE dr.request_status_job_id_seq TO dr_role;


--
-- Name: DEFAULT PRIVILEGES FOR SEQUENCES; Type: DEFAULT ACL; Schema: dr; Owner: dbo
--

ALTER DEFAULT PRIVILEGES FOR ROLE dbo IN SCHEMA dr REVOKE ALL ON SEQUENCES  FROM dbo;
ALTER DEFAULT PRIVILEGES FOR ROLE dbo IN SCHEMA dr GRANT ALL ON SEQUENCES  TO dr_role;


--
-- Name: DEFAULT PRIVILEGES FOR TYPES; Type: DEFAULT ACL; Schema: dr; Owner: dbo
--

ALTER DEFAULT PRIVILEGES FOR ROLE dbo IN SCHEMA dr REVOKE ALL ON TYPES  FROM PUBLIC;
ALTER DEFAULT PRIVILEGES FOR ROLE dbo IN SCHEMA dr REVOKE ALL ON TYPES  FROM dbo;
ALTER DEFAULT PRIVILEGES FOR ROLE dbo IN SCHEMA dr GRANT ALL ON TYPES  TO dr_role;


--
-- Name: DEFAULT PRIVILEGES FOR FUNCTIONS; Type: DEFAULT ACL; Schema: dr; Owner: dbo
--

ALTER DEFAULT PRIVILEGES FOR ROLE dbo IN SCHEMA dr REVOKE ALL ON FUNCTIONS  FROM PUBLIC;
ALTER DEFAULT PRIVILEGES FOR ROLE dbo IN SCHEMA dr REVOKE ALL ON FUNCTIONS  FROM dbo;
ALTER DEFAULT PRIVILEGES FOR ROLE dbo IN SCHEMA dr GRANT ALL ON FUNCTIONS  TO dr_role;


--
-- Name: DEFAULT PRIVILEGES FOR TABLES; Type: DEFAULT ACL; Schema: dr; Owner: dbo
--

ALTER DEFAULT PRIVILEGES FOR ROLE dbo IN SCHEMA dr REVOKE ALL ON TABLES  FROM dbo;
ALTER DEFAULT PRIVILEGES FOR ROLE dbo IN SCHEMA dr GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,UPDATE ON TABLES  TO dr_role;


--
-- PostgreSQL database dump complete
--

